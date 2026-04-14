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
});
