document.addEventListener("DOMContentLoaded", function(event) {
    const toggleBtn = document.getElementById("menu-toggle");
    if(toggleBtn) {
        toggleBtn.addEventListener("click", function(e) {
            e.preventDefault();
            document.getElementById("wrapper").classList.toggle("toggled");
        });
    }

    const darkModeBtn = document.getElementById("darkModeToggle");
    const body = document.body;
    
    if (localStorage.getItem("darkMode") === "enabled") {
        body.classList.add("dark-mode");
    }

    if(darkModeBtn) {
        darkModeBtn.addEventListener("click", () => {
            body.classList.toggle("dark-mode");
            if (body.classList.contains("dark-mode")) {
                localStorage.setItem("darkMode", "enabled");
            } else {
                localStorage.setItem("darkMode", "disabled");
            }
            
            // If Chart.js is present, we might want to update chart colors but we'll stick to a simple refresh for brevity
            // location.reload(); // Optional if charts don't update well
        });
    }

    // Custom Cursor Logic
    const cursorDot = document.querySelector('.cursor-dot');
    const cursorOutline = document.querySelector('.cursor-outline');
    
    if (cursorDot && cursorOutline) {
        window.addEventListener('mousemove', function(e) {
            const posX = e.clientX;
            const posY = e.clientY;
            
            cursorDot.style.left = `${posX}px`;
            cursorDot.style.top = `${posY}px`;
            
            // Trailing effect using Web Animations API for extremely smooth follow
            cursorOutline.animate({
                left: `${posX}px`,
                top: `${posY}px`
            }, { duration: 300, fill: "forwards" });
        });

        // Add hover effects universally via delegation
        document.body.addEventListener('mouseover', function(e) {
            if (e.target.closest('a, button, input, select, .heatmap-cell, .list-group-item, .glass-card, .btn')) {
                cursorOutline.style.transform = 'translate(-50%, -50%) scale(1.5)';
                cursorOutline.style.backgroundColor = 'rgba(186, 191, 148, 0.2)'; /* Accent hover */
                cursorOutline.style.borderColor = 'rgba(186, 191, 148, 0.8)';
            }
        });

        document.body.addEventListener('mouseout', function(e) {
            if (e.target.closest('a, button, input, select, .heatmap-cell, .list-group-item, .glass-card, .btn')) {
                cursorOutline.style.transform = 'translate(-50%, -50%) scale(1)';
                cursorOutline.style.backgroundColor = 'transparent';
                cursorOutline.style.borderColor = 'var(--color-primary)';
            }
        });
    }
});
