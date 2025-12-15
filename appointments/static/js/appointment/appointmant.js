
    // --- GLOBAL VARIABLES ---
    let currentStep = 1;

    // ==========================================
    // 1. NAVIGATION & STEPPER LOGIC
    // ==========================================
    
    function showStep(step) {
        // Hide all steps
        document.querySelectorAll('.form-section').forEach(el => el.classList.add('hidden'));
        
        // Show current step
        const targetStep = document.getElementById(`step-content-${step}`);
        if(targetStep) {
            targetStep.classList.remove('hidden');
            updateStepperUI(step);
            currentStep = step;
        }
    }

    function nextStep(step) {
        // Validate current step before moving forward
        if(validateStep(currentStep)) {
            showStep(step);
        }
    }

    function prevStep(step) {
        showStep(step);
    }

    function handleHeaderBack() {
        if (currentStep === 1) {
            // Go to home if on first step
            window.location.href = "{% url 'home' %}";
        } else {
            // Go back one step
            prevStep(currentStep - 1);
        }
    }

    function updateStepperUI(activeStep) {
        for (let i = 1; i <= 4; i++) {
            const stepEl = document.getElementById(`step-indicator-${i}`);
            const lineEl = document.getElementById(`line-${i-1}`);
            
            // Reset Classes
            if(stepEl) stepEl.classList.remove('active', 'completed');
            if (lineEl) lineEl.classList.remove('completed');
            
            // Apply Logic
            if (i < activeStep) {
                // Completed Steps
                stepEl.classList.add('completed');
                stepEl.querySelector('.num').classList.add('hidden');
                stepEl.querySelector('.icon').classList.remove('hidden');
                if (lineEl) lineEl.classList.add('completed');
            } else if (i === activeStep) {
                // Active Step
                stepEl.classList.add('active');
                stepEl.querySelector('.num').classList.remove('hidden');
                stepEl.querySelector('.icon').classList.add('hidden');
                if (lineEl) lineEl.classList.add('completed');
            } else {
                // Future Steps
                stepEl.querySelector('.num').classList.remove('hidden');
                stepEl.querySelector('.icon').classList.add('hidden');
            }
        }
    }

    // ==========================================
    // 2. VALIDATION LOGIC
    // ==========================================

    function validateStep(step) {
        const section = document.getElementById(`step-content-${step}`);
        // Find inputs that are VISIBLE and REQUIRED
        // (Hidden inputs might be in other steps, so we scope to 'section')
        const inputs = section.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            // Check if empty
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#ef4444'; // Red border
            } else {
                input.style.borderColor = '#e5e7eb'; // Default border
            }
        });

        // Special Check for Step 2 (Time Slot)
        if (step === 2) {
            const timeSlot = document.getElementById('selectedTimeSlot').value;
            if (!timeSlot) {
                isValid = false;
                alert("Please select a time slot.");
            }
        }

        if (!isValid && step !== 2) { // Step 2 has its own alert
            alert('Please fill in all required fields.');
        }
        return isValid;
    }

    // ==========================================
    // 3. SELECTION & SUMMARY LOGIC
    // ==========================================

    function selectTime(element, timeString) {
        // 1. Visual Update
        document.querySelectorAll('.time-slot').forEach(el => el.classList.remove('selected'));
        element.classList.add('selected');
        
        // 2. Data Update (Hidden Input)
        document.getElementById('selectedTimeSlot').value = timeString;
        
        // 3. Update Summary Card
        updateSummary();
    }

    function selectPayment(element, method) {
        document.querySelectorAll('.payment-option').forEach(el => el.classList.remove('active'));
        element.classList.add('active');
        document.getElementById('selectedPaymentMethod').value = method;
    }

    function updateSummary() {
        // Get Elements
        const doctorSelect = document.getElementById('doctorSelect');
        const dateInput = document.getElementById('dateInput');
        const timeInput = document.getElementById('selectedTimeSlot');
        
        // --- FIX: Correct ID for Fee Display ---
        const feeDisplay = document.getElementById('summaryFee'); 

        // 1. Update Doctor Name & Fee
        if (doctorSelect.selectedIndex > 0) {
            const selectedOption = doctorSelect.options[doctorSelect.selectedIndex];
            
            // Update Name
            const fullText = selectedOption.text;
            // Optional: Extract just name if text is "Dr. Name - Cardio (Fee)"
            const doctorName = fullText.split('-')[0].trim(); 
            document.getElementById('summaryDoctor').innerText = doctorName;

            // Update Fee
            const fee = selectedOption.getAttribute('data-fee');
            if (fee && feeDisplay) {
                feeDisplay.innerText = "NPR " + fee;
            }
        }

        // 2. Update Date
        if (dateInput && dateInput.value) {
            document.getElementById('summaryDate').innerText = dateInput.value;
        }

        // 3. Update Time
        if (timeInput && timeInput.value) {
            document.getElementById('summaryTime').innerText = timeInput.value;
        }
    }

    // ==========================================
    // 4. INITIALIZATION
    // ==========================================
    
    // Run once page loads to set default states if needed
    document.addEventListener('DOMContentLoaded', function() {
        // Ensure inputs are reset or loaded correctly
        updateStepperUI(1);
    });