# codex – Social Learning for Coders
code z is a community-driven platform where developers and engineers collaborate to solve coding challenges, debug broken snippets, and discuss algorithmic efficiency. Unlike traditional competitive platforms, IdeaHub prioritizes the "Social" aspect of learning through a Reddit-inspired feed
# CodeZ Django Project
# code z

![IdeaHub Logo](ideahub_logo%20.png)

A platform where ideas meet code.
## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install django pillow
```

### 2. Run Migrations
```bash
cd codez_project
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (to add problems via admin)
```bash
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

---

## 📄 Pages & URLs

| URL | View | Description |
|-----|------|-------------|
| `/` | `home_view` | Homepage — problem feed (login required) |
| `/login/` | `login_view` | Login page |
| `/register/` | `register_view` | Registration page |
| `/logout/` | `logout_view` | Logout (redirects to login) |
| `/profile/` | `profile_view` | Your own profile (login required) |
| `/profile/<username>/` | `profile_view` | Any user's profile (login required) |
| `/admin/` | Django admin | Add/edit problems, users |

---

## 🔗 Avatar → Profile Navigation

The navbar avatar on the homepage is linked to the user's profile page:

```html
<!-- In home.html nav -->
<a href="{% url 'my_profile' %}" class="nav-avatar-btn">
  <div class="...avatar...">{{ request.user.username|first|upper }}</div>
</a>
```

Clicking the avatar takes the logged-in user to `/profile/`.

---

## 🎨 Styling

All pages follow the same **indigo/purple dark theme**:
- Background: `#07071a` / `#0d0d1a`
- Accent: `#6366f1` (indigo), `#8b5cf6` (violet)
- Font: DM Sans + JetBrains Mono
- Tailwind CSS (CDN) + custom CSS variables

---

## 🗃️ Models

**UserProfile** — extends Django's `User`:
- `bio`, `avatar`, `location`
- `github_url`, `linkedin_url`, `twitter_url`
- `rating` (default 1500), `problems_solved`, `streak`
- `rank`, `is_online`

**Problem**:
- `title`, `slug`, `description`
- `difficulty` (easy/medium/hard)
- `tags` (JSON list)
- `upvotes`, `acceptance_rate`
- `is_premium`

---

## ➕ Adding Problems

1. Go to `/admin/`
2. Log in with superuser credentials
3. Click **Problems → Add Problem**
4. Fill in title, slug, description, difficulty, tags (as JSON list e.g. `["arrays", "loops"]`)

---

## 🔒 Authentication Flow

```
Unauthenticated → / → redirects to /login/
Login success → redirects to / (homepage)
Register → auto-login → redirects to /
Logout → redirects to /login/
```


## Authors
- [LOHITH A.S](https://github.com/mr-lohith)
- [ARYAN JAYAN MENON ](https://github.com/aryanjm1405)
- [SOURAV SURESH](https://github.com/souravofficialx)

## Appendix

Any additional information goes here

