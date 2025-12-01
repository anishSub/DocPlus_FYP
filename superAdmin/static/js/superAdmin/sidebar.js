document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });

        document.addEventListener('click', function(event) {
            const isClickInside = sidebar.contains(event.target);
            const isClickOnToggle = menuToggle.contains(event.target);
            
            if (sidebar.classList.contains('active') && !isClickInside && !isClickOnToggle && window.innerWidth <= 1024) {
                sidebar.classList.remove('active');
            }
        });
    }
});