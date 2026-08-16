// ==========================================
// 1. Отримання CSRF-токена
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
// 2. Фільтрація пошуку
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

window.filterFriendsList = function() {
    const input = document.getElementById('friend-search-input');
    if (input) runFriendsFilter(input.value);
};

document.addEventListener('input', function (e) {
    if (e.target && e.target.id === 'friend-search-input') {
        runFriendsFilter(e.target.value);
    }
});

// ==========================================
// 3. Надіслати запит
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
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            btnElement.textContent = 'Надіслано';
            btnElement.className = 'px-3.5 py-1.5 bg-[#2f2f2f] text-gray-400 font-semibold text-xs rounded-full cursor-not-allowed flex-shrink-0';
        } else {
            btnElement.disabled = false;
            btnElement.textContent = originalText;
            alert(data.message || 'Помилка');
        }
    })
    .catch(err => {
        btnElement.disabled = false;
        btnElement.textContent = originalText;
    });
};

// ==========================================
// 4. Прийняти запит
// ==========================================
window.acceptFriendRequest = function(requestId, btnElement) {
    if (!btnElement) return;
    
    btnElement.disabled = true;
    btnElement.textContent = '...';

    fetch(`/friends/accept/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
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
            btnElement.textContent = 'Прийняти';
            alert(data.message || 'Помилка прийняття');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        btnElement.disabled = false;
        btnElement.textContent = 'Прийняти';
    });
};

// ==========================================
// 5. Відхилити запит
// ==========================================
window.rejectFriendRequest = function(requestId, btnElement) {
    if (!btnElement) return;
    btnElement.disabled = true;

    fetch(`/friends/reject/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            const card = document.getElementById(`request-card-${requestId}`);
            if (card) card.remove();

            const remainingCount = data.remaining_count !== undefined ? data.remaining_count : 0;
            window.updatePendingBadge(remainingCount);
        } else {
            btnElement.disabled = false;
        }
    });
};

// ==========================================
// 6. Оновлення бейджів сповіщень
// ==========================================
window.updatePendingBadge = function(count) {
    const badges = document.querySelectorAll('#add-friends-btn span, nav span');
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
// 7. Додавання друга у ліву панель 
// ==========================================
window.addFriendToChatsList = function(friend) {
    const chatsContainer = document.getElementById('chats-list');
    if (!chatsContainer) return;

    if (document.getElementById(`chat-item-${friend.id}`)) return;

    // Видаляємо блок "У вас немає чатів", якщо він є
    const emptyPlaceholder = chatsContainer.querySelector('.text-center');
    if (emptyPlaceholder) emptyPlaceholder.remove();

    const firstLetter = friend.username ? friend.username.charAt(0).toUpperCase() : '?';
    const avatarImgHtml = friend.avatar_url 
        ? `<img src="${friend.avatar_url}" onerror="this.remove()" class="absolute inset-0 w-full h-full object-cover rounded-full">`
        : '';

    const newChatHtml = `
        <div id="chat-item-${friend.id}" class="flex items-center justify-between p-3 rounded-xl hover:bg-[#1c1c1c] transition group cursor-pointer">
            <div class="flex items-center space-x-3 flex-1 min-w-0">
                <div class="relative flex-shrink-0 w-12 h-12 flex items-center justify-center">
                    <div class="w-full h-full rounded-full bg-yellow-500 flex items-center justify-center text-lg font-bold text-black uppercase overflow-hidden relative">
                        <span>${firstLetter}</span>
                        ${avatarImgHtml}
                    </div>
                </div>

                <div class="flex-1 min-w-0 pr-2">
                    <h4 class="font-semibold text-sm truncate">${friend.username}</h4>
                    <p class="text-xs text-gray-400 flex items-center" id="chat-status-text-${friend.id}">
                        <span class="w-2 h-2 rounded-full bg-green-500 inline-block mr-1.5 flex-shrink-0"></span>
                        <span>Новий друг • Розпочніть спілкування</span>
                    </p>
                </div>
            </div>
        </div>
    `;

    chatsContainer.insertAdjacentHTML('beforeend', newChatHtml);
};