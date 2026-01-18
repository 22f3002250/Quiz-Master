# 🎯 Quiz Management System (Flask + Vue)

A full-stack **Quiz Management System** built using **Flask** for the backend and **Vue.js (Vite)** for the frontend.
The application supports **admin and user roles**, quiz creation, participation, scoring, and background task processing using **Celery**.

---

## 🚀 Features

### 👤 User Features

* User registration and login
* Browse available quizzes
* Attempt quizzes and submit answers
* View scores and performance
* Manage user profile

### 🛠️ Admin Features

* Admin authentication
* Create, update, and delete:

  * Subjects
  * Chapters
  * Quizzes
* Manage users
* View quiz reports and analytics

### ⚙️ Background Tasks

* Scheduled reminders using **Celery**
* Logging of reminder tasks
* Asynchronous task execution

---

## 🏗️ Tech Stack

### Backend

* **Python**
* **Flask**
* **SQLite**
* **Celery**
* **Redis** (for Celery broker)
* Flask Extensions (Blueprints, SQLAlchemy, etc.)

### Frontend

* **Vue.js 3**
* **Vite**
* **Vue Router**
* **HTML, CSS**

---

## 📁 Project Structure

```
code/
│
├── backend/
│   ├── app.py               # Main Flask application
│   ├── model.py             # Database models
│   ├── extensions.py        # Flask extensions
│   ├── celery_worker.py     # Celery background tasks
│   ├── requirements.txt     # Backend dependencies
│   ├── instance/
│   │   └── quiz.db          # SQLite database
│   └── reminders.log        # Celery task logs
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── views/           # Admin & User views
│   │   └── assets/
│   └── public/
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/quiz-management-system.git
cd quiz-management-system
```

---

### 2️⃣ Backend Setup (Flask)

```bash
cd code/backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the Flask app:

```bash
python app.py
```

Backend will run at:

```
http://127.0.0.1:5000/
```

---

### 3️⃣ Frontend Setup (Vue + Vite)

```bash
cd code/frontend
npm install
npm run dev
```

Frontend will run at:

```
http://localhost:5173/
```

---

### 4️⃣ Celery & Redis (Optional – for background tasks)

Start Redis:

```bash
redis-server
```

Run Celery worker:

```bash
cd code/backend
celery -A celery_worker.celery worker --loglevel=info
```

---

## 🧪 Database

* Uses **SQLite**
* Database file located at:

```
backend/instance/quiz.db
```



