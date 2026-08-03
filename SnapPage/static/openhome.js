function openSnap(url, snapId) {
    const mainContent = document.getElementById('main-content');
    
    mainContent.innerHTML = `
        <div class="flex items-center justify-center h-full text-gray-400">
            <p class="animate-pulse">Завантаження...</p>
        </div>
    `;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            mainContent.innerHTML = html;

            // Виконуємо вкладені теги <script> із завантаженого HTML
            const scripts = mainContent.querySelectorAll('script');
            scripts.forEach(oldScript => {
                const newScript = document.createElement('script');
                Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                oldScript.parentNode.replaceChild(newScript, oldScript);
            });

            // Оновлюємо статус в лівій панелі на "Відкрито"
            const icon = document.getElementById(`snap-icon-${snapId}`);
            const label = document.getElementById(`status-label-${snapId}`);
            if (icon && label) {
                icon.className = "w-2.5 h-2.5 border-2 border-blue-500 rounded-sm inline-block mr-1";
                label.innerText = "Відкрито";
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            mainContent.innerHTML = `
                <div class="text-center text-red-400 space-y-2">
                    <p class="font-semibold">Не вдалося завантажити снап.</p>
                    <p class="text-xs text-gray-500">${error.message}</p>
                </div>
            `;
        });
}

// Змінна для зберігання таймера (щоб скидати, якщо користувач клікнув на інший снап раніше часу)
let activeSnapTimeout = null;

function runSilentSnapTimer(seconds) {
    // Якщо вже був активний таймер — скасовуємо його
    if (activeSnapTimeout) {
        clearTimeout(activeSnapTimeout);
    }

    // Перетворюємо секунди в мілісекунди
    const ms = seconds * 1000;

    // Запускаємо прихований таймер
    activeSnapTimeout = setTimeout(() => {
        closeSnap();
    }, ms);
}

function closeSnap() {
    const mainContent = document.getElementById('main-content');
    
    // Повертаємо початковий десктопний стан
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