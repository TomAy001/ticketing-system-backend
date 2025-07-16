// ICT Center Ticketing System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize WebSocket connection for real-time notifications
    initializeWebSocket();
    
    // Initialize alert close buttons
    initializeAlerts();
    
    // Initialize form enhancements
    initializeForms();
});

// WebSocket for real-time notifications
function initializeWebSocket() {
    if (!window.location.pathname.includes('login') && !window.location.pathname.includes('register') && window.location.pathname !== '/') {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        try {
            const socket = new WebSocket(wsUrl);
            
            socket.onopen = function(e) {
                console.log('WebSocket connection established');
            };
            
            socket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                if (data.type === 'ticket_notification') {
                    showNotification(data.message, 'info');
                }
            };
            
            socket.onclose = function(e) {
                console.log('WebSocket connection closed');
                // Attempt to reconnect after 5 seconds
                setTimeout(initializeWebSocket, 5000);
            };
            
            socket.onerror = function(e) {
                console.error('WebSocket error:', e);
            };
        } catch (error) {
            console.log('WebSocket not available:', error);
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    notification.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
            <div class="notification-content">
                <strong style="display:block; margin-bottom: 0.25rem;">
                    ${type === 'success' ? 'Success!' : type === 'error' ? 'Error!' : type === 'warning' ? 'Warning!' : 'Info'}
                </strong>
                <p style="margin: 0;">${message}</p>
            </div>
            <button class="notification-close" onclick="this.closest('.notification').remove()">×</button>
        </div>
    `;

    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}


// Initialize alert close buttons
function initializeAlerts() {
    document.querySelectorAll('.alert-close').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
}

// Initialize form enhancements
function initializeForms() {
    // Add loading states to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Processing...';
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.textContent = submitButton.getAttribute('data-original-text') || 'Submit';
                }, 5000);
            }
        });
        
        // Store original button text
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.setAttribute('data-original-text', submitButton.textContent);
        }
    });
    
    // Add character counter for textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'character-counter';
            counter.style.fontSize = '0.75rem';
            counter.style.color = 'var(--text-secondary)';
            counter.style.marginTop = '0.25rem';
            textarea.parentElement.appendChild(counter);
            
            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${remaining} characters remaining`;
                
                if (remaining < 50) {
                    counter.style.color = 'var(--warning-color)';
                } else if (remaining < 10) {
                    counter.style.color = 'var(--error-color)';
                } else {
                    counter.style.color = 'var(--text-secondary)';
                }
            }
            
            textarea.addEventListener('input', updateCounter);A
            updateCounter();
        }
    });
    // This one's gonna Auto-fill dem fields based on ID Number
    const idInput = document.getElementById("id_id_number");
    if (idInput) {
        idInput.addEventListener("blur", function () {
            const id = this.value.trim().toUpperCase();
            if (id.length > 5) {
                fetch(`/get-student-info/?id_number=${id}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.found) {
                            const firstNameInput = document.getElementById("id_first_name");
                            const lastNameInput = document.getElementById("id_last_name");
                            const departmentInput = document.getElementById("id_department");
                            
                            if (firstNameInput) firstNameInput.value = data.first_name;
                            if (lastNameInput) lastNameInput.value = data.last_name;
                            if (departmentInput) departmentInput.value = data.department;
                        } else {
                            showNotification("ID number not found in university records.", "warning");
                        }
                    })
                    .catch(error => {
                        console.error("Failed to fetch student info:", error);
                        showNotification("An error occurred while checking ID number.", "error");
                    });
            }
        });
    }  
}

// Utility functions for AJAX requests
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function makeAjaxRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX request failed:', error);
            showNotification('An error occurred. Please try again.', 'error');
            throw error;
        });
}

// Format date and time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
}

// Auto-refresh certain pages
function autoRefresh() {
    if (window.location.pathname.includes('dashboard') || window.location.pathname.includes('admin-panel')) {
        // Refresh page every 5 minutes
        setTimeout(() => {
            window.location.reload();
        }, 300000);
    }
}

// Initialize auto-refresh
autoRefresh();

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 500);
        });
    }
}

function performSearch(query) {
    if (!query.trim()) {
        return;
    }
    
    // Implement search logic here
    console.log('Searching for:', query);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+/ or Cmd+/ to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals/notifications
    if (e.key === 'Escape') {
        const notifications = document.querySelectorAll('.notification');
        notifications.forEach(notification => notification.remove());
    }
});

// Progressive Web App support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Performance monitoring
function measurePageLoad() {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const navigation = performance.getEntriesByType('navigation')[0];
            const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
            
            if (loadTime > 3000) {
                console.warn('Page load time exceeded 3 seconds:', loadTime + 'ms');
            }
        }, 0);
    });
}

measurePageLoad();

// Accessibility enhancements
function initializeAccessibility() {
    // Add skip links
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--primary-color);
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add main content ID if it doesn't exist
    const mainContent = document.querySelector('.main-content');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
}

initializeAccessibility();