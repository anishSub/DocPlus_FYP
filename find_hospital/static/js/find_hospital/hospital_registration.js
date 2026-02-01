var currentTab = 0;
showTab(currentTab);

function showTab(n) {
    var x = document.getElementsByClassName("form-step");

    // Hide all steps
    for (let i = 0; i < x.length; i++) {
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

    // Submit if at end (Now Step 3 is Review, submit after that)
    if (currentTab + n >= x.length) {
        document.getElementById("hospitalRegForm").submit();
        return false;
    }

    currentTab = currentTab + n;

    // If moving to Review Step (Index 3), populate data
    if (currentTab == 3) {
        populateReviewSummary();
    }

    showTab(currentTab);
}

function populateReviewSummary() {
    // 1. Identity
    document.getElementById('summary_name').innerText = document.getElementById('rev_name').value;
    document.getElementById('summary_type').innerText = document.getElementById('rev_type').value;
    document.getElementById('summary_year').innerText = document.getElementById('rev_year').value;
    document.getElementById('summary_phone').innerText = document.getElementById('rev_phone').value;
    document.getElementById('summary_email').innerText = document.getElementById('rev_email').value;
    document.getElementById('summary_city').innerText = document.getElementById('rev_city').value;
    document.getElementById('summary_district').innerText = document.getElementById('rev_district').value;

    // 2. Details
    document.getElementById('summary_beds').innerText = document.getElementById('rev_beds').value;

    // 3. Hours
    let start = document.getElementById('rev_opd_start').value;
    let end = document.getElementById('rev_opd_end').value;
    document.getElementById('summary_hours').innerText = start + ' - ' + end;

    // 4. Emergency
    let emergency = document.getElementById('emergency_toggle').checked ? "Yes (24/7)" : "No";
    document.getElementById('summary_emergency').innerText = emergency;

    // 5. Services (Checkboxes)
    let services = [];
    document.querySelectorAll('input[name="services"]:checked').forEach((checkbox) => {
        services.push(checkbox.value);
    });

    // Add Departments too
    let depts = document.getElementById('hiddenDeptField').value;
    if (depts) services.push(...depts.split(','));

    document.getElementById('summary_services').innerText = services.join(', ') || "None Selected";
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
        if (hiddenDept.value == "") {
            alert("Please add at least one department.");
            valid = false;
        }
    }

    return valid;
}

function updateStepper(n) {
    var steps = document.getElementsByClassName("step");
    var lines = document.getElementsByClassName("line");

    // Define icons for each step (matching HTML)
    const icons = [
        '<i class="far fa-building"></i>',       // Step 0: Identity
        '<i class="fas fa-procedures"></i>',     // Step 1: Capacity
        '<i class="far fa-image"></i>',          // Step 2: Media
        '<i class="fas fa-check"></i>'           // Step 3: Review
    ];

    for (var i = 0; i < steps.length; i++) {
        steps[i].classList.remove("active", "completed");

        // Reset to default icon first
        steps[i].querySelector('.circle').innerHTML = icons[i];

        if (i == n) {
            steps[i].classList.add("active");
        } else if (i < n) {
            steps[i].classList.add("completed");
            // Completed steps show checkmark
            steps[i].querySelector('.circle').innerHTML = '<i class="fas fa-check"></i>';
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

    departments.forEach(function (dept) {
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
    if (file) {
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