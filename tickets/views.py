from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.core.paginator import Paginator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import *
from .forms import *
import pandas as pd
import requests
from io import StringIO

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def create_admin_user(request):
    if User.objects.filter(username='admin').exists():
        return HttpResponse("Superuser already exists.")
    
    User.objects.create_superuser('admin', 'admin@run.edu.ng', 'adminpassword123')
    return HttpResponse("Superuser created.")

def load_csv_from_google_drive():
    url = 'https://drive.usercontent.google.com/u/0/uc?id=1SJ3gZ4JocS0YFz4c2O8PIjI63h6pwijp&export=download'
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print("Error loading Google Drive CSV:", e)
        return None
    
def test_csv_columns(request):
    df = load_csv_from_google_drive()
    if df is not None:
        return JsonResponse({'columns': df.columns.tolist()})
    return JsonResponse({'error': 'Failed to load CSV'}, status=500)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            id_number = form.cleaned_data.get('id_number').strip().upper()
            df = load_csv_from_google_drive()

            if df is not None:
                match = df[df['ID NUMBER'].astype(str).str.strip().str.upper() == id_number]
                
                if not match.empty:
                    dept = match.iloc[0]['DEPARTMENT'].strip()
                    role = 'staff' if dept.upper() == 'DICT' else 'student'

                    try:
                        with transaction.atomic():
                            user = form.save()
                            UserProfile.objects.create(
                                user=user,
                                role=role,
                                department=dept,
                                phone_number=form.cleaned_data.get('phone_number', '')
                            )
                            messages.success(request, 'Account created successfully. You can now log in.')
                            return redirect('login')
                    except Exception as e:
                        form.add_error(None, f'An unexpected error occurred: {str(e)}')
                else:
                    form.add_error('id_number', 'This ID is not recognized in university records.')
            else:
                form.add_error(None, 'Failed to load university records. Please try again later.')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def get_student_info(request):
    id_number = request.GET.get('id_number', '').strip().upper()
    df = load_csv_from_google_drive()

    if df is not None:
        match = df[df['ID NUMBER'].astype(str).str.strip().str.upper() == id_number]

        if not match.empty:
            dept = match.iloc[0]['DEPARTMENT'].strip()
            role = 'staff' if dept.upper() == 'DICT' else 'student'

            data = {
                'first_name': match.iloc[0]['FIRST NAME'],
                'last_name': match.iloc[0]['LAST NAME'],
                'department': dept,
                'role': role,
                'found': True
            }
        else:
            data = {'found': False}
    else:
        data = {'found': False}

    return JsonResponse(data)

@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    
    if user_profile.role == 'admin':
        tickets = Ticket.objects.all()
        stats = {
            'total_tickets': Ticket.objects.count(),
            'pending_tickets': Ticket.objects.filter(status='pending').count(),
            'in_progress_tickets': Ticket.objects.filter(status='in_progress').count(),
            'resolved_tickets': Ticket.objects.filter(status='resolved').count(),
        }
    elif user_profile.role == 'staff':
        tickets = Ticket.objects.filter(assigned_to=request.user)
        stats = {
            'assigned_tickets': tickets.count(),
            'pending_tickets': tickets.filter(status='pending').count(),
            'in_progress_tickets': tickets.filter(status='in_progress').count(),
            'resolved_tickets': tickets.filter(status='resolved').count(),
        }
    else: 
        tickets = Ticket.objects.filter(created_by=request.user)
        stats = {
            'my_tickets': tickets.count(),
            'pending_tickets': tickets.filter(status='pending').count(),
            'in_progress_tickets': tickets.filter(status='in_progress').count(),
            'resolved_tickets': tickets.filter(status='resolved').count(),
        }
    
    recent_tickets = tickets[:5]
    
    context = {
        'user_profile': user_profile,
        'stats': stats,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'dashboard.html', context)

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            
            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'notifications',
                {
                    'type': 'ticket_notification',
                    'message': f'New ticket created: {ticket.ticket_id}',
                    'ticket_id': ticket.ticket_id,
                    'action': 'created'
                }
            )
            
            messages.success(request, f'Ticket {ticket.ticket_id} created successfully!')
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = TicketForm()
    return render(request, 'create_ticket.html', {'form': form})

@login_required
def ticket_list(request):
    user_profile = request.user.userprofile
    
    if user_profile.role == 'admin':
        tickets = Ticket.objects.all()
    elif user_profile.role == 'staff':
        tickets = Ticket.objects.filter(assigned_to=request.user)
    else:
        tickets = Ticket.objects.filter(created_by=request.user)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Filter by category if provided
    category_filter = request.GET.get('category')
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_profile': user_profile,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'ticket_list.html', context)

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    user_profile = request.user.userprofile
    staff_users = User.objects.filter(userprofile__role='staff').order_by('username')
    
    # Check permissions
    if (user_profile.role == 'student' and ticket.created_by != request.user) or \
       (user_profile.role == 'staff' and ticket.assigned_to != request.user and ticket.created_by != request.user):
        messages.error(request, 'You do not have permission to view this ticket.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        comment_form = TicketCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('ticket_detail', ticket_id=ticket_id)
    else:
        comment_form = TicketCommentForm()
    
    context = {
        'ticket': ticket,
        'user_profile': user_profile,
        'comment_form': comment_form,
        'staff_users': staff_users,
    }
    return render(request, 'ticket_detail.html', context)

@login_required
def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        user_profile = request.user.userprofile

        if user_profile.role not in ['admin', 'staff']:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Ticket.STATUS_CHOICES]
        if not new_status or new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status value'}, status=400)

        ticket.status = new_status
        ticket.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications',
            {
                'type': 'ticket_notification',
                'message': f'Ticket {ticket.ticket_id} status updated to {new_status}',
                'ticket_id': ticket.ticket_id,
                'action': 'status_updated',
                'new_status': new_status
            }
        )

        return JsonResponse({'success': True, 'new_status': new_status})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def assign_ticket(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
        user_profile = request.user.userprofile
        
        # Only admins can assign tickets
        if user_profile.role != 'admin':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        staff_id = request.POST.get('staff_id')
        if staff_id:
            staff_user = get_object_or_404(User, id=staff_id)
            ticket.assigned_to = staff_user
            ticket.status = 'assigned'
            ticket.save()
            
            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'notifications',
                {
                    'type': 'ticket_notification',
                    'message': f'Ticket {ticket.ticket_id} assigned to {staff_user.get_full_name() or staff_user.username}',
                    'ticket_id': ticket.ticket_id,
                    'action': 'assigned'
                }
            )
            
            return JsonResponse({'success': True})
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def admin_panel(request):
    user_profile = request.user.userprofile
    if user_profile.role != 'admin':
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('dashboard')
    
    # Get all users and their profiles
    users = User.objects.select_related('userprofile').all()
    tickets = Ticket.objects.all()[:10]  # Recent tickets
    staff_users = User.objects.filter(userprofile__role='staff')
    
    context = {
        'users': users,
        'tickets': tickets,
        'staff_users': staff_users,
    }
    return render(request, 'admin_panel.html', context)

@login_required
@permission_required('tickets.delete_ticket', raise_exception=True)
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        ticket.delete()
        return redirect('home')  # or wherever you want to redirect after deletion

    return render(request, 'confirm_delete.html', {'ticket': ticket})

#error handlers
def custom_bad_request(request, exception=None):
    return render(request, '400.html', status=400)

def custom_permission_denied(request, exception=None):
    return render(request, '403.html', status=403)

def custom_page_not_found(request, exception=None):
    return render(request, '404.html', status=404)

def custom_server_error(request):
    return render(request, '500.html', status=500)
