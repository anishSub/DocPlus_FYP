var currentTab = 0; 
showTab(currentTab); 

function showTab(n) {
    var x = document.getElementsByClassName("form-step");
    
    // Hide all steps
    for(let i=0; i<x.length; i++) {
        x[i].style.display = "none";
        x[i].classList.remove('active');
    }
    
    // Show current step
    x[n].style.display = "block";
    // Small delay to allow CSS animation to trigger
    setTimeout(() => x[n].classList.add('active'), 10);

    // Update Buttons
    if (n == 0) {
        document.getElementById("prevBtn").style.display = "none";
    } else {
        document.getElementById("prevBtn").style.display = "inline-flex";
    }

    if (n == (x.length - 1)) {
        document.getElementById("nextBtn").innerHTML = '<i class="fas fa-check-circle"></i> Submit Registration';
        document.getElementById("nextBtn").style.background = "#10B981"; // Green for submit
    } else {
        document.getElementById("nextBtn").innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        document.getElementById("nextBtn").style.background = "#1C398E"; // Blue for next
    }

    updateStepper(n);
}

function nextPrev(n) {
    var x = document.getElementsByClassName("form-step");
    
    // Validate if pressing Next
    if (n == 1 && !validateForm()) return false;
    
    // Submit if at end
    if (currentTab + n >= x.length) {
        document.getElementById("hospitalRegForm").submit();
        return false;
    }
    
    currentTab = currentTab + n;
    showTab(currentTab);
}

function validateForm() {
    var x, y, i, valid = true;
    x = document.getElementsByClassName("form-step");
    // Get all inputs and selects in current tab
    y = x[currentTab].querySelectorAll("input, select, textarea");
    
    for (i = 0; i < y.length; i++) {
        // Check if empty and required
        if (y[i].hasAttribute('required') && y[i].value.trim() == "") {
            y[i].className += " invalid";
            valid = false;
        } else {
            y[i].classList.remove("invalid");
        }
    }

    // Special Check for Step 1 (Departments)
    if (currentTab == 1) {
        let hiddenDept = document.getElementById("hiddenDeptField");
        if(hiddenDept.value == "") {
            alert("Please add at least one department.");
            valid = false;
        }
    }

    return valid; 
}

function updateStepper(n) {
    var steps = document.getElementsByClassName("step");
    var lines = document.getElementsByClassName("line");

    for (var i = 0; i < steps.length; i++) {
        steps[i].classList.remove("active", "completed");
        
        if (i == n) {
            steps[i].classList.add("active");
        } else if (i < n) {
            steps[i].classList.add("completed");
            // Change circle to checkmark
            steps[i].querySelector('.circle').innerHTML = '<i class="fas fa-check"></i>';
        } else {
            // Reset numbers if going back
            steps[i].querySelector('.circle').innerHTML = (i + 1);
        }
    }
}

// --- DEPARTMENT TAG LOGIC ---
var departments = [];

function addDepartment() {
    var input = document.getElementById("deptInput");
    var value = input.value.trim();

    if (value && !departments.includes(value)) {
        departments.push(value);
        renderTags();
        input.value = "";
    }
}

function removeDepartment(value) {
    departments = departments.filter(item => item !== value);
    renderTags();
}

function renderTags() {
    var container = document.getElementById("deptTagsContainer");
    var hiddenField = document.getElementById("hiddenDeptField");
    
    container.innerHTML = "";
    
    departments.forEach(function(dept) {
        var tag = document.createElement("div");
        tag.className = "dept-tag";
        tag.innerHTML = `${dept} <i class="fas fa-times" onclick="removeDepartment('${dept}')"></i>`;
        container.appendChild(tag);
    });

    // Update hidden input for backend
    hiddenField.value = departments.join(",");
}

// File Preview
function previewFile(input) {
    var file = input.files[0];
    if(file){
        document.getElementById("file-preview-name").innerText = "Selected: " + file.name;
    }
}

// --- Password Toggle Function ---
function togglePassword(fieldId, icon) {
    const input = document.getElementById(fieldId);
    
    if (input.type === "password") {
        // Show Password
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        // Hide Password
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}