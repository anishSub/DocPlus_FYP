# DocPlus - Healthcare App in Nepal 🏥💙

**DocPlus** is a comprehensive Healthcare Information and Management System built with **Django**. It connects patients with doctors and hospitals, offering a seamless platform for booking appointments, managing schedules, handling payments, and conducting secure telehealth consultations.

Designed with a focus on usability and robust backend integrations, DocPlus features dedicated dashboards for Patients, Doctors, Hospital Administrators, and Super Admins.

---

## 🌟 Key Features

### 1. Multi-Role Dashboards
- **🧑‍⚕️ Doctors**: Manage schedules, view daily appointments, track earnings, and moderate patient reviews.
- **🏥 Hospitals**: Track incoming leads, manage affiliated doctors, and view hospital-specific analytics (traffic, click-through rates, and estimated bed capacity).
- **🧍 Patients**: Book appointments, filter doctors by specialty, maintain profiles, and view upcoming/past consultations.
- **⚙️ Super Admin**: Oversee the entire platform, verify new doctors and hospitals, moderate reviews, and track platform-wide revenue and analytics.

### 2. Telehealth & Real-Time Communication
- **📹 Video Consultations**: Integrated with the **Jitsi Meet API** for secure, high-quality, in-browser video calls. No external application downloads required. Patient and Doctor are automatically routed to unique, secure meeting rooms.
- **💬 Live Chat**: Real-time WebSocket-based messaging powered by **Django Channels**. Allows patients and doctors to communicate instantly during video calls with a persistent chat history.

### 3. Integrated Payment Gateways
- **💳 Khalti & eSewa**: Complete integration with Nepal's leading digital wallets. Patients can securely pay for their appointments online. The system accurately separates "Scheduled" vs "Paid" status and tracks revenue dynamically.

### 4. Smart Search & Filtering
- Dynamic, database-driven filtering allows patients to find doctors by specialty, hospital affiliation, and rating.
- Built-in location search and categorical breakdowns to easily surface healthcare providers.

---

## 💻 Tech Stack

- **Backend**: Python, Django, Django Channels (WebSockets)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), FontAwesome
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **APIs & Integrations**: 
  - Jitsi Meet External API (Video)
  - Khalti API (Payments)
  - eSewa API (Payments)
- **Real-Time Layers**: Daphne (ASGI Server), Redis (Channel Layer for WebSockets)

---

## 📋 Installation & Setup (Local Development)

Follow these steps to get DocPlus running on your local machine:

1. **Clone the repository**
   ```bash
   git clone https://github.com/anishSub/DocPlus_FYP.git
   cd DocPlus_FYP
   ```

2. **Create and activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   *Note: Because the app uses Django Channels for WebSockets, `runserver` automatically utilizes the Daphne ASGI server.*

6. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 🔐 System Architecture Notes

- **URL Routing**: The system strictly uses Django's `{% url %}` structures ensuring absolute pathing, which prevents interference from Chrome Extensions during JavaScript `fetch()` calls.
- **Dynamic Contexts**: Nearly all dashboard metrics (Revenue, Clicks, Pending Approvals, Active Doctors) are calculated in real-time via Django ORM aggregation, preventing stale or static dummy data.

---
*Developed as a Final Year Project (FYP)*
