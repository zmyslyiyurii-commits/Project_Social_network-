document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatar-input');
    
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const preview = document.getElementById('avatar-preview');
                    if (preview.tagName === 'IMG') {
                        preview.src = e.target.result;
                    } else {
                        const newImg = document.createElement('img');
                        newImg.id = 'avatar-preview';
                        newImg.src = e.target.result;
                        newImg.className = 'w-full h-full rounded-full object-cover border-4 border-[#EAB308] shadow-lg shadow-yellow-500/20';
                        preview.parentNode.replaceChild(newImg, preview);
                    }
                };
                
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }
});