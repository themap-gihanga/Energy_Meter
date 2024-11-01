// static/js/notifications.js
document.addEventListener('DOMContentLoaded', function() {
    // WebSocket connection
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const notificationSocket = new WebSocket(
        ws_scheme + '://' + window.location.host + '/ws/notifications/'
    );

    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        addNotification(data);
        updateNotificationCount();
    };

    function addNotification(notification) {
        const notificationList = document.getElementById('notification-list');
        const notificationHtml = `
            <li class="notification-item">
                <i class="bi bi-${getNotificationIcon(notification.type)} text-${getNotificationColor(notification.type)}"></i>
                <div>
                    <h4>${notification.title}</h4>
                    <p>${notification.message}</p>
                    <p>${notification.timestamp}</p>
                </div>
            </li>
            <li><hr class="dropdown-divider"></li>
        `;
        notificationList.insertAdjacentHTML('afterbegin', notificationHtml);
    }

    function getNotificationIcon(type) {
        switch(type) {
            case 'add': return 'plus-circle';
            case 'update': return 'pencil-square';
            case 'delete': return 'trash';
            default: return 'bell';
        }
    }

    function getNotificationColor(type) {
        switch(type) {
            case 'add': return 'success';
            case 'update': return 'primary';
            case 'delete': return 'danger';
            default: return 'secondary';
        }
    }

    // Search functionality
    const searchForm = document.getElementById('searchForm');
    const searchModal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
    const searchResults = document.getElementById('searchResults');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            searchResults.innerHTML = data.html;
            searchModal.show();
        })
        .catch(error => console.error('Error:', error));
    });
});