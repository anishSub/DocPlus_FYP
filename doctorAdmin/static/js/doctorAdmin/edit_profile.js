/*  You do not have to move the whole script back to the HTML file. You can keep your JavaScript clean and separate.

The problem is that Django cannot read external .js files. It only scans .html templates. So when your external JS file has {% url ... %}, Django ignores it, and the browser tries to read it as literal text, which causes the 404 error.

Here is the professional way to fix this while keeping your JS in a separate file.

<script>
    // 1. Pass Django URLs to a global JavaScript variable
    const SCHEDULE_CONFIG = {
        urls: {
            get: "{% url 'get_schedule' %}",
            add: "{% url 'add_schedule' %}",
            delete: "{% url 'delete_schedule' %}"
        },
        csrfToken: "{{ csrf_token }}" // Pass the token here too!
    };
</script>
*/

let currentDay = 'Sun'; // Default

// 1. Load Day Logic
function loadDay(day) {
    currentDay = day;
    document.getElementById('active-day-label').innerText = getFullDay(day) + " Schedule";
    
    // Highlight active tab
    document.querySelectorAll('.day-tab').forEach(btn => {
        btn.classList.remove('active');
        if(btn.innerText === day) btn.classList.add('active');
    });

    // --- FIX 1: Use the Variable, NOT the Django Tag ---
    fetch(`${SCHEDULE_CONFIG.urls.get}?day=${day}`)
        .then(res => res.json())
        .then(data => renderSlots(data.schedules))
        .catch(err => console.error("Error loading schedule:", err));
}

// 2. Render Slots to HTML
function renderSlots(schedules) {
    const container = document.getElementById('slots-container');
    container.innerHTML = '';

    if (!schedules || schedules.length === 0) {
        container.innerHTML = '<p class="no-slots-msg">No time slots added for this day.</p>';
        return;
    }

    schedules.forEach(slot => {
        // Clean up time string (take first 5 chars: "09:00:00" -> "09:00")
        let start = slot.start_time.substring(0, 5);
        let end = slot.end_time.substring(0, 5);
        
        let html = `
            <div class="slot-item">
                <span><i class="far fa-clock"></i> ${start} - ${end}</span>
                <button type="button" class="btn-delete-slot" onclick="deleteSlot(${slot.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        container.innerHTML += html;
    });
}

// 3. Add Slot Logic
function addSlot() {
    const start = document.getElementById('new-start').value;
    const end = document.getElementById('new-end').value;

    if(!start || !end) { alert("Please select start and end times"); return; }

    // --- FIX 2: Use Config URL and Config Token ---
    fetch(SCHEDULE_CONFIG.urls.add, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": SCHEDULE_CONFIG.csrfToken 
        },
        body: JSON.stringify({ day: currentDay, start_time: start, end_time: end })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            loadDay(currentDay); // Refresh list
            document.getElementById('new-start').value = ''; // Clear inputs
            document.getElementById('new-end').value = '';
        } else {
            alert("Error adding slot: " + data.message);
        }
    });
}

// 4. Delete Slot Logic
function deleteSlot(id) {
    if(!confirm("Remove this time slot?")) return;

    // --- FIX 3: Use Config URL and Config Token ---
    fetch(SCHEDULE_CONFIG.urls.delete, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json", 
            "X-CSRFToken": SCHEDULE_CONFIG.csrfToken 
        },
        body: JSON.stringify({ id: id })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') loadDay(currentDay);
    });
}

// Helper for Day Names
function getFullDay(short) {
    const map = { 'Sun': 'Sunday', 'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday' };
    return map[short] || short;
}

// Load Sunday by default on open
document.addEventListener('DOMContentLoaded', () => loadDay('Sun'));

