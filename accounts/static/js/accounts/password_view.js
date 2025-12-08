
  function togglePassword(fieldId, icon) {
        const input = document.getElementById(fieldId);
        
        if (input.type === "password") {
            input.type = "text"; // Show
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        } else {
            input.type = "password"; // Hide
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
        }
    }
