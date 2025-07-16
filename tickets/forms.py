from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import *

# Validator for ID number
ID_validator = RegexValidator(
    regex=r'^RUN(?:/[A-Z0-9]{2,}){2,5}/\d{2,}$',
    message='ID number must follow a valid institutional format like RUN/ARC/23/12345 or RUN/REG/SS/PF/12345'
)


class UserRegistrationForm(UserCreationForm):
    id_number = forms.CharField(
        max_length=20,
        required=True,
        label='ID Number',
        validators=[ID_validator],
        help_text='Format: RUN/CMP/21/12345'
    )
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:
            id_num = self.data.get('id_number', '').strip().upper()
            record = StudentRecord.objects.filter(id_number=id_num).first()
            if record:
                self.fields['first_name'].initial = record.first_name
                self.fields['last_name'].initial = record.surname
                self.fields['department'].initial = record.department.upper()

                # Assign role based on department
                assigned_role = 'staff' if record.department.strip().upper() == 'DICT' else 'student'
                self.fields['role'].initial = assigned_role
                self.fields['role'].widget.attrs['readonly'] = True  # Make it readonly in HTML
                self.fields['role'].widget.attrs['style'] = 'background-color: #f9f9f9;'  # Optional grey background

                self.fields['first_name'].widget.attrs['readonly'] = True
                self.fields['last_name'].widget.attrs['readonly'] = True
                self.fields['department'].widget.attrs['readonly'] = True

                # Save role on form instance for later use in save()
                self.assigned_role = assigned_role




    def clean_id_number(self):
        id_num = self.cleaned_data['id_number'].strip().upper()
        if not StudentRecord.objects.filter(id_number=id_num).exists():
            raise forms.ValidationError("ID not found in university records.")
        return id_num

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.lower().endswith('@run.edu.ng'):
            raise forms.ValidationError("Please use your institutional email address (e.g., yourname@run.edu.ng).")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role=getattr(self, 'assigned_role', 'student'),
                department=self.cleaned_data['department'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the problem'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }

class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }

