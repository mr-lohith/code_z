# CodeZ – Django Project Setup

## 📁 Project Structure
```
codez_project/
├── manage.py
├── requirements.txt
├── db.sqlite3          ← created after migrate
├── codez_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── codez/
    ├── views.py        ← login, register, home, profile logic
    ├── urls.py         ← all URL routes
    ├── templates/
    │   └── codez/
    │       ├── login.html      ✅ New – styled login page
    │       ├── register.html   ✅ New – styled register page
    │       ├── home.html       ✅ Your original HomePage.html (Django connected)
    │       └── profile.html    ✅ Your original UserProfile.html (Django connected)
```

## 🚀 How to Run on Windows

### Step 1 – Install Python
Download from python.org → **check "Add Python to PATH"**

### Step 2 – Open Command Prompt
Win + R → type `cmd` → Enter

### Step 3 – Install Django
```
pip install django
```

### Step 4 – Extract ZIP & navigate
```
cd Desktop\codez_project
```

### Step 5 – Create database
```
python manage.py migrate
```

### Step 6 – Create admin user
```
python manage.py createsuperuser
```

### Step 7 – Run server
```
python manage.py runserver
```

### Step 8 – Open browser
| Page | URL |
|------|-----|
| Login | http://127.0.0.1:8000/login/ |
| Register | http://127.0.0.1:8000/register/ |
| Home Feed | http://127.0.0.1:8000/ |
| My Profile | http://127.0.0.1:8000/profile/ |
| Admin | http://127.0.0.1:8000/admin/ |

## 🔗 What's Connected
- **Avatar (TH)** on HomePage → clicks through to your Profile page
- **Back to Feed** on Profile → goes back to HomePage
- **Login/Register** → full authentication with session
- **Logout** → clears session, redirects to login
- All pages are **protected** – unauthenticated users go to /login/
