document.addEventListener('DOMContentLoaded', () => {
    const gradientText = document.querySelector('.animated-gradient-text');
    if (!gradientText) return;

    const animationSpeed = 8; 
    const animationDuration = animationSpeed * 1000;
    let elapsed = 0;
    let lastTime = null;

    function animate(time) {
        if (lastTime === null) {
            lastTime = time;
            requestAnimationFrame(animate);
            return;
        }

        const deltaTime = time - lastTime;
        lastTime = time;
        elapsed += deltaTime;

        const fullCycle = animationDuration * 2;
        const cycleTime = elapsed % fullCycle;
        let progress = 0;

        if (cycleTime < animationDuration) {
            progress = (cycleTime / animationDuration) * 100;
        } else {
            progress = 100 - ((cycleTime - animationDuration) / animationDuration) * 100;
        }

        gradientText.style.backgroundPosition = `${progress}% 50%`;
        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
});