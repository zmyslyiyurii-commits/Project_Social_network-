let activeSnapTimeout = null;

// Отримання CSRF-токена з cookie для AJAX-запитів
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Очищення активного таймера снапу
function clearSnapTimer() {
    if (activeSnapTimeout) {
        clearTimeout(activeSnapTimeout);
        activeSnapTimeout = null;
    }
}

// Відкриття та AJAX-завантаження вмісту снапу
function openSnap(url, snapId, status) {
    if (status === 'opened') {
        console.log('Снап уже переглянуто.');
        return; 
    }

    clearSnapTimer();

    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;

    mainContent.innerHTML = `
        <div class="flex items-center justify-center h-full text-gray-400">
            <p class="animate-pulse">Завантаження...</p>
        </div>
    `;

    fetch(url)
        .then(response => {
            if (response.redirected) throw new Error('Сервер повернув редірект.');
            if (response.status === 403) throw new Error('Цей снап уже переглянуто.');
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return response.text();
        })
        .then(html => {
            if (html.includes('<!DOCTYPE html>') || html.includes('<aside')) {
                throw new Error('Отримано повну сторінку замість картки снапу.');
            }

            mainContent.innerHTML = html;

            // Виконання inline-скриптів із завантаженого шаблону
            executeScripts(mainContent);

            // Оновлення індикатора стану в списку
            const icon = document.getElementById(`snap-icon-${snapId}`);
            const label = document.getElementById(`status-label-${snapId}`);
            const snapItem = document.getElementById(`snap-item-${snapId}`);

            if (icon && label) {
                icon.className = "w-2.5 h-2.5 border-2 border-blue-500 rounded-sm inline-block mr-1 bg-transparent flex-shrink-0";
                label.innerText = "Відкрито";
            }

            if (snapItem) {
                snapItem.setAttribute('onclick', `openSnap('${url}', ${snapId}, 'opened')`);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            mainContent.innerHTML = `
                <div class="text-center text-red-400 space-y-2 p-6">
                    <p class="font-semibold">Не вдалося завантажити снап.</p>
                    <p class="text-xs text-gray-500">${error.message}</p>
                </div>
            `;
        });
}

// Запуск таймера автоматичного закриття снапу
function runSilentSnapTimer(seconds) {
    clearSnapTimer();
    const ms = seconds * 1000;
    activeSnapTimeout = setTimeout(() => {
        closeSnap();
    }, ms);
}

// Закриття снапу
function closeSnap() {
    resetMainContent();
}

// Повертає стандартне привітання в праву панель
function resetMainContent() {
    clearSnapTimer();

    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;

    mainContent.innerHTML = `
        <div class="text-center space-y-4">
            <div class="w-24 h-24 rounded-full bg-[#2a2a2a] flex items-center justify-center text-[#fffc00] mx-auto shadow-lg ring-4 ring-[#252525]">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13.997 4a2 2 0 0 1 1.76 1.05l.486.9A2 2 0 0 0 18.003 7H20a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1.997a2 2 0 0 0 1.759-1.048l.489-.904A2 2 0 0 1 10.004 4z"/><circle cx="12" cy="13" r="3"/></svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-200">Почніть спілкування</h3>
            <p class="text-sm text-gray-500 max-w-sm">Оберіть друга зі списку ліворуч, щоб переглянути його снапи або історії.</p>
        </div>
    `;
}

// Відкриває форму створення снапу
function openCreateSnap() {
    clearSnapTimer();
    const mainContent = document.getElementById('main-content');
    const template = document.getElementById('snap-form-template');
    if (!mainContent || !template) return;

    mainContent.innerHTML = '';
    mainContent.appendChild(template.content.cloneNode(true));
}

// Відкриває форму створення історії
function openCreateStory() {
    clearSnapTimer();
    const mainContent = document.getElementById('main-content');
    const template = document.getElementById('story-form-template');
    if (!mainContent || !template) return;

    mainContent.innerHTML = '';
    mainContent.appendChild(template.content.cloneNode(true));
}

// Оновлює назву обраного файлу для снапу
function updateSnapFileName(input) {
    const label = document.getElementById('snapFileName');
    if (label && input.files && input.files[0]) {
        label.textContent = input.files[0].name;
    }
}

// Оновлює назву обраного файлу для історії
function updateStoryFileName(input) {
    const label = document.getElementById('storyFileName');
    if (label && input.files && input.files[0]) {
        label.textContent = input.files[0].name;
    }
}

// Допоміжна функція перезапуску скриптів після AJAX-встави HTML
function executeScripts(container) {
    const scripts = container.querySelectorAll('script');
    scripts.forEach(oldScript => {
        const newScript = document.createElement('script');
        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });
}

// ================= СИСТЕМА ДОДАВАННЯ ДРУЗІВ =================

// Відкриття панелі друзів у правому блоці
function openAddFriendsPanel() {
    clearSnapTimer();

    const mainContent = document.getElementById('main-content');
    const addBtn = document.getElementById('add-friends-btn');
    if (!mainContent) return;

    const url = addBtn ? addBtn.getAttribute('data-url') : '/friends/add/';

    mainContent.innerHTML = `
        <div class="flex items-center justify-center h-full text-gray-400">
            <p class="animate-pulse">Завантаження панелі друзів...</p>
        </div>
    `;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            return response.text();
        })
        .then(html => {
            mainContent.innerHTML = html;
            executeScripts(mainContent);
        })
        .catch(error => {
            console.error('Error loading add friends panel:', error);
            mainContent.innerHTML = `
                <div class="text-center text-red-400 p-6">
                    <p class="font-semibold">Не вдалося завантажити панель друзів.</p>
                </div>
            `;
        });
}

// Надіслати запит у друзі
function sendFriendRequest(userId, btnElement) {
    const csrftoken = getCookie('csrftoken');
    btnElement.disabled = true;
    btnElement.innerText = 'Надсилання...';

    fetch(`/friends/send/${userId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            btnElement.innerText = 'Запит надіслано';
            btnElement.className = 'px-3 py-1.5 rounded-full bg-gray-700 text-xs text-gray-300 cursor-not-allowed';
        } else {
            alert(data.message || 'Помилка надсилання');
            btnElement.disabled = false;
            btnElement.innerText = '+ Додати';
        }
    })
    .catch(err => {
        console.error(err);
        btnElement.disabled = false;
        btnElement.innerText = '+ Додати';
    });
}

// Прийняти запит
function acceptFriendRequest(requestId, btnElement) {
    const csrftoken = getCookie('csrftoken');

    fetch(`/friends/accept/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            const card = document.getElementById(`request-card-${requestId}`);
            if (card) card.remove();
        } else {
            alert(data.message || 'Помилка виконання');
        }
    })
    .catch(err => console.error(err));
}

// Відхилити запит
function rejectFriendRequest(requestId, btnElement) {
    const csrftoken = getCookie('csrftoken');

    fetch(`/friends/reject/${requestId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            const card = document.getElementById(`request-card-${requestId}`);
            if (card) card.remove();
        } else {
            alert(data.message || 'Помилка виконання');
        }
    })
    .catch(err => console.error(err));
}