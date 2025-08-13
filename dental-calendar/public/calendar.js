let calendar;
let socket;

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeCalendar();
    setupEventListeners();
});

function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    // Real-time appointment events
    socket.on('appointmentCreated', function(appointment) {
        console.log('New appointment created:', appointment);
        calendar.refetchEvents();
        showNotification(`✅ New appointment: ${appointment.patient_name}`, 'success');
    });
    
    socket.on('appointmentUpdated', function(data) {
        console.log('Appointment updated:', data);
        calendar.refetchEvents();
        showNotification('📝 Appointment updated', 'info');
    });
    
    socket.on('appointmentDeleted', function(data) {
        console.log('Appointment deleted:', data);
        calendar.refetchEvents();
        showNotification('🗑️ Appointment deleted', 'warning');
    });
}

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'multiMonthYear,dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day',
            year: 'Year'
        },
        locale: 'en',
        firstDay: 1, // Monday
        slotMinTime: '08:00:00',
        slotMaxTime: '18:00:00',
        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
            startTime: '08:00',
            endTime: '18:00'
        },
        height: 'auto',
        events: '/api/appointments',
        
        // Event styling
        eventDisplay: 'block',
        dayMaxEvents: 4,
        moreLinkClick: 'popover',
        
        // Click handlers
        dateClick: function(info) {
            openNewAppointmentModal(info.dateStr);
        },
        
        eventClick: function(info) {
            showAppointmentDetails(info.event);
        },
        
        // Drag and drop
        editable: true,
        eventDrop: function(info) {
            updateAppointmentTime(info.event);
        },
        
        eventResize: function(info) {
            updateAppointmentTime(info.event);
        },
        
        // Custom event rendering
        eventContent: function(arg) {
            const props = arg.event.extendedProps;
            return {
                html: `
                    <div style="padding: 2px 4px;">
                        <strong>${props.patientName}</strong><br>
                        <small>${props.treatmentType || 'Appointment'}</small>
                    </div>
                `
            };
        }
    });
    
    calendar.render();
}

function setupEventListeners() {
    // Form submission
    document.getElementById('appointmentForm').addEventListener('submit', function(e) {
        e.preventDefault();
        createAppointment();
    });
    
    // Modal close on outside click
    window.addEventListener('click', function(e) {
        const modal = document.getElementById('appointmentModal');
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Set today as default date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('appointmentDate').value = today;
}

function openNewAppointmentModal(date = null) {
    const modal = document.getElementById('appointmentModal');
    
    if (date) {
        document.getElementById('appointmentDate').value = date;
    }
    
    // Clear form
    document.getElementById('appointmentForm').reset();
    const today = new Date().toISOString().split('T')[0];
    if (!date) {
        document.getElementById('appointmentDate').value = today;
    }
    
    modal.style.display = 'block';
    document.getElementById('patientName').focus();
}

function closeModal() {
    document.getElementById('appointmentModal').style.display = 'none';
}

function createAppointment() {
    const formData = {
        patient_name: document.getElementById('patientName').value,
        phone: document.getElementById('patientPhone').value,
        date: document.getElementById('appointmentDate').value,
        time: document.getElementById('appointmentTime').value,
        end_time: calculateEndTime(document.getElementById('appointmentTime').value, 30),
        treatment_type: document.getElementById('treatmentType').value,
        notes: document.getElementById('notes').value
    };
    
    fetch('/api/appointments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showNotification('❌ Error: ' + data.error, 'error');
        } else {
            showNotification('✅ Appointment successfully created!', 'success');
            closeModal();
            calendar.refetchEvents();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Connection error', 'error');
    });
}

function showAppointmentDetails(event) {
    const props = event.extendedProps;
    const startTime = new Date(event.start).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    const date = new Date(event.start).toLocaleDateString('en-US');
    
    const details = `
        📅 ${date} at ${startTime}
        👤 ${props.patientName}
        📞 ${props.phone || 'No phone'}
        🦷 ${props.treatmentType || 'General'}
        📝 ${props.notes || 'No notes'}
        ✅ Status: ${getStatusText(props.status)}
    `;
    
    if (confirm(`${details}\n\nWould you like to delete this appointment?`)) {
        deleteAppointment(event.id);
    }
}

function deleteAppointment(appointmentId) {
    fetch(`/api/appointments/${appointmentId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('🗑️ Appointment deleted', 'success');
            calendar.refetchEvents();
        } else {
            showNotification('❌ Error deleting', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Connection error', 'error');
    });
}

function updateAppointmentTime(event) {
    const newDate = event.start.toISOString().split('T')[0];
    const newTime = event.start.toISOString().split('T')[1].substring(0, 5);
    const endTime = event.end ? event.end.toISOString().split('T')[1].substring(0, 5) : calculateEndTime(newTime, 30);
    
    fetch(`/api/appointments/${event.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: newDate,
            time: newTime,
            end_time: endTime,
            status: event.extendedProps.status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('📝 Appointment moved', 'success');
        } else {
            showNotification('❌ Error moving appointment', 'error');
            calendar.refetchEvents(); // Revert on error
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Connection error', 'error');
        calendar.refetchEvents(); // Revert on error
    });
}

function refreshCalendar() {
    calendar.refetchEvents();
    showNotification('🔄 Calendar updated', 'info');
}

function showToday() {
    calendar.today();
    showNotification('📅 Showing today', 'info');
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    if (connected) {
        statusEl.textContent = '🟢 Connected - Live Updates';
        statusEl.className = 'connection-status connected';
    } else {
        statusEl.textContent = '🔴 Disconnected';
        statusEl.className = 'connection-status disconnected';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        z-index: 1001;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Set color based on type
    switch(type) {
        case 'success':
            notification.style.background = '#28a745';
            break;
        case 'error':
            notification.style.background = '#dc3545';
            break;
        case 'warning':
            notification.style.background = '#ffc107';
            notification.style.color = '#000';
            break;
        default:
            notification.style.background = '#17a2b8';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function calculateEndTime(startTime, durationMinutes) {
    const [hours, minutes] = startTime.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes + durationMinutes;
    const endHours = Math.floor(totalMinutes / 60);
    const endMins = totalMinutes % 60;
    return `${endHours.toString().padStart(2, '0')}:${endMins.toString().padStart(2, '0')}`;
}

function getStatusText(status) {
    switch(status) {
        case 'confirmed': return 'Confirmed';
        case 'cancelled': return 'Cancelled';
        case 'completed': return 'Completed';
        default: return status;
    }
}