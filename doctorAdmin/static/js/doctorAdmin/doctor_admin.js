document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    // Safety check to ensure elements exist before running logic
    if (menuToggle && sidebar) {
        
        // Toggle Sidebar on Menu Button Click
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent click from bubbling to document
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside (UX improvement for mobile)
        document.addEventListener('click', function(event) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = menuToggle.contains(event.target);
            
            // If sidebar is open, and user clicks outside of it, close it
            if (sidebar.classList.contains('active') && !isClickInsideSidebar && !isClickOnToggle && window.innerWidth <= 1024) {
                sidebar.classList.remove('active');
            }
        });
    }
});