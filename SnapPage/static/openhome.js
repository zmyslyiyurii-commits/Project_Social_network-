 // Змінна для зберігання активного таймера
let activeSnapTimeout = null;

function openSnap(url, snapId, status) {
    // 1. Якщо снап вже відкрито (через атрибут або стан) — блокуємо повторний запит
    if (status === 'opened') {
        console.log('Снап уже переглянуто, повторне відкриття заблоковано.');
        return; 
    }

    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;

    // 2. Індикація завантаження
    mainContent.innerHTML = `
        <div class="flex items-center justify-center h-full text-gray-400">
            <p class="animate-pulse">Завантаження...</p>
        </div>
    `;

    // 3. Запит на сервер
    fetch(url)
        .then(response => {
            // Якщо сервер спробував зробити редірект (наприклад, на home)
            if (response.redirected) {
                throw new Error('Сервер повернув редірект замість картки снапу.');
            }
            // Якщо views.py повернув 403 Forbidden (снап вже в статусі 'opened' в БД)
            if (response.status === 403) {
                throw new Error('Цей снап уже був переглянутый.');
            }
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            // Перевірка: якщо сервер раптом віддав повну HTML-сторінку замість фрагмента
            if (html.includes('<!DOCTYPE html>') || html.includes('<aside')) {
                throw new Error('Сервер повернув повну сторінку замість картки снапу.');
            }

            // Вставляємо HTML снапу в праву панель
            mainContent.innerHTML = html;

            // 4. Динамічно виконуємо всі вкладені теги <script> (запускає runSilentSnapTimer)
            const scripts = mainContent.querySelectorAll('script');
            scripts.forEach(oldScript => {
                const newScript = document.createElement('script');
                Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                oldScript.parentNode.replaceChild(newScript, oldScript);
            });

            // 5. Оновлюємо іконку та статус у лівому списку
            const icon = document.getElementById(`snap-icon-${snapId}`);
            const label = document.getElementById(`status-label-${snapId}`);
            const snapItem = document.getElementById(`snap-item-${snapId}`);

            if (icon && label) {
                icon.className = "w-2.5 h-2.5 border-2 border-blue-500 rounded-sm inline-block mr-1 bg-transparent";
                label.innerText = "Відкрито";
            }

            // 6. Оновлюємо атрибут onclick у DOM, щоб наступні кліки без F5 одразу блокувалися
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

function runSilentSnapTimer(seconds) {
    // Якщо вже був запущений таймер від попереднього снапу — скидаємо його
    if (activeSnapTimeout) {
        clearTimeout(activeSnapTimeout);
    }

    // Запускаємо новий таймер автоматичного закриття
    const ms = seconds * 1000;
    activeSnapTimeout = setTimeout(() => {
        closeSnap();
    }, ms);
}

function closeSnap() {
    // Скасовуємо таймер, якщо снап закривається ручною кнопкою
    if (activeSnapTimeout) {
        clearTimeout(activeSnapTimeout);
        activeSnapTimeout = null;
    }

    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;
    
    // Повертаємо базовий десктопний стан правої панелі
    mainContent.innerHTML = `
        <div class="text-center space-y-4">
            <div class="w-24 h-24 rounded-full bg-[#2a2a2a] flex items-center justify-center text-[#fffc00] mx-auto shadow-lg ring-4 ring-[#252525]">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13.997 4a2 2 0 0 1 1.76 1.05l.486.9A2 2 0 0 0 18.003 7H20a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1.997a2 2 0 0 0 1.759-1.048l.489-.904A2 2 0 0 1 10.004 4z"/><circle cx="12" cy="13" r="3"/></svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-200">Перегляд завершено</h3>
            <p class="text-sm text-gray-500 max-w-sm">Час перегляду снапу вичерпано. Оберіть інший чат зі списку.</p>
        </div>
    `;
}