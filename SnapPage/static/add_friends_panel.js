// ==========================================
// 1. Отримання CSRF-токена (Cookie / DOM)
// ==========================================
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    if (!cookieValue) {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) cookieValue = csrfInput.value;
    }
    return cookieValue;
}

// ==========================================
// 2. Логіка фільтрації пошуку
// ==========================================
function runFriendsFilter(query) {
    const filter = (query || '').toLowerCase().trim();
    const items = document.querySelectorAll('.user-search-item, [id^="request-card-"]');

    items.forEach(item => {
        let username = item.getAttribute('data-username');
        if (!username) {
            const nameEl = item.querySelector('.font-semibold');
            username = nameEl ? nameEl.textContent.toLowerCase().trim() : '';
        }

        if (username.includes(filter)) {
            item.classList.remove('hidden');
            item.classList.add('flex');
        } else {
            item.classList.remove('flex');
            item.classList.add('hidden');
        }
    });
}

// Глобальна функція фільтрації для прямого виклику
window.filterFriendsList = function() {
    const input = document.getElementById('friend-search-input');
    if (input) runFriendsFilter(input.value);
};

// Автоматичне слухання введення у полі пошуку
document.addEventListener('input', function (e) {
    if (e.target && e.target.id === 'friend-search-input') {
        runFriendsFilter(e.target.value);
    }
});

// ==========================================
// 3. Відправка запиту у друзі
// ==========================================
window.sendFriendRequest = function(userId, btnElement) {
    if (!btnElement) return;
    
    const originalText = btnElement.textContent;
    btnElement.disabled = true;

    fetch(`/friends/send/${userId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(async res => {
        if (!res.ok) throw new Error(`Помилка сервера: ${res.status}`);
        return res.json();
    })
    .then(data => {
        if (data.status === 'success') {
            btnElement.textContent = 'Надіслано';
            btnElement.className = 'px-3.5 py-1.5 bg-[#2f2f2f] text-gray-400 font-semibold text-xs rounded-full cursor-not-allowed flex-shrink-0';
        } else {
            btnElement.disabled = false;
            btnElement.textContent = originalText;
            alert(data.message || 'Не вдалося надіслати запит');
        }
    })
    .catch(err => {
        console.error('sendFriendRequest error:', err);
        btnElement.disabled = false;
        btnElement.textContent = originalText;
        alert('Помилка виконання: ' + err.message);
    });
};

// ==========================================
// 4. Прийняття запиту у друзі
// ==========================================
window.acceptFriendRequest = function(requestId, btnElement) {
    if (!btnElement) return;
    
    const originalText = btnElement.textContent;
    btnElement.disabled = true;
    btnElement.textContent = '...';

    fetch(`/friends/accept/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(async res => {
        if (!res.ok) throw new Error(`Помилка сервера: ${res.status}`);
        return res.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const card = document.getElementById(`request-card-${requestId}`);
            if (card) card.remove();

            const remainingCount = data.remaining_count !== undefined ? data.remaining_count : 0;
            window.updatePendingBadge(remainingCount);

            if (data.friend) {
                window.addFriendToChatsList(data.friend);
            }
        } else {
            btnElement.disabled = false;
            btnElement.textContent = originalText;
            alert(data.message || 'Не вдалося прийняти запит');
        }
    })
    .catch(err => {
        console.error('acceptFriendRequest error:', err);
        btnElement.disabled = false;
        btnElement.textContent = originalText;
        alert('Помилка виконання: ' + err.message);
    });
};

// ==========================================
// 5. Відхилення запиту у друзі
// ==========================================
window.rejectFriendRequest = function(requestId, btnElement) {
    if (!btnElement) return;
    
    const originalText = btnElement.textContent;
    btnElement.disabled = true;

    fetch(`/friends/reject/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(async res => {
        if (!res.ok) throw new Error(`Помилка сервера: ${res.status}`);
        return res.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const card = document.getElementById(`request-card-${requestId}`);
            if (card) card.remove();

            const remainingCount = data.remaining_count !== undefined ? data.remaining_count : 0;
            window.updatePendingBadge(remainingCount);
        } else {
            btnElement.disabled = false;
            btnElement.textContent = originalText;
            alert(data.message || 'Не вдалося відхилити запит');
        }
    })
    .catch(err => {
        console.error('rejectFriendRequest error:', err);
        btnElement.disabled = false;
        btnElement.textContent = originalText;
        alert('Помилка виконання: ' + err.message);
    });
};

// ==========================================
// 6. Оновлення бейджів та лічильників
// ==========================================
window.updatePendingBadge = function(count) {
    const titleCount = document.getElementById('pending-requests-count-title');
    if (titleCount) titleCount.textContent = count;

    const section = document.getElementById('pending-requests-section');
    if (section && count === 0) {
        section.classList.add('hidden');
    }

    const badges = document.querySelectorAll('.pending-badge, #pending-badge, [data-pending-count]');
    badges.forEach(badge => {
        if (count > 0) {
            badge.textContent = count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    });
};

// ==========================================
// 7. Додавання нового друга в список чатів
// ==========================================
window.addFriendToChatsList = function(friend) {
    const chatsContainer = document.querySelector('#chats-container, .chats-container, #chats-list');
    if (!chatsContainer) return;

    if (document.getElementById(`chat-item-${friend.id}`)) return;

    const avatarHtml = friend.avatar_url
        ? `<img src="${friend.avatar_url}" class="w-full h-full object-cover rounded-full">`
        : `<span>${friend.username.charAt(0).toUpperCase()}</span>`;

    const newChatHtml = `
        <div id="chat-item-${friend.id}" class="flex items-center justify-between p-3 bg-[#1e1e1e] hover:bg-[#282828] border border-[#262626] rounded-xl transition cursor-pointer">
            <div class="flex items-center space-x-3 min-w-0">
                <div class="w-11 h-11 rounded-full bg-yellow-500 flex items-center justify-center font-bold text-black uppercase flex-shrink-0 relative">
                    ${avatarHtml}
                </div>
                <div class="min-w-0">
                    <p class="font-bold text-sm text-white truncate">${friend.username}</p>
                    <p class="text-xs text-gray-400 truncate">Новий друг</p>
                </div>
            </div>
        </div>
    `;

    chatsContainer.insertAdjacentHTML('afterbegin', newChatHtml);
};