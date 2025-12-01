document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Select Elements
    const timeSlots = document.querySelectorAll('.time-slot');
    const hiddenInput = document.getElementById('selectedTimeSlot');
    const form = document.querySelector('form');

    // 2. Add Click Logic to Time Slots
    if (timeSlots.length > 0) {
        timeSlots.forEach(slot => {
            slot.addEventListener('click', function() {
                // A. Reset: Remove 'selected' class from ALL slots
                timeSlots.forEach(s => s.classList.remove('selected'));

                // B. Highlight: Add 'selected' class to the clicked slot
                // This triggers the .selected CSS to make it blue
                this.classList.add('selected');

                // C. Save: Update the hidden input value
                if (hiddenInput) {
                    const value = this.getAttribute('data-value');
                    hiddenInput.value = value;
                }
            });
        });
    }

    // 3. Form Validation (Prevents going Next without a time)
    if (form) {
        form.addEventListener('submit', function(e) {
            // If the hidden input is empty, stop the form
            if (hiddenInput && !hiddenInput.value) {
                e.preventDefault(); 
                alert("Please select a time slot.");
                
                // Optional: Scroll back to the time slots
                const grid = document.querySelector('.time-slot-grid');
                if (grid) grid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }
});