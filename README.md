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
# CodeZ — Social Coding Learning Platform

A Reddit-style community platform for coders to ask questions, share projects,
solve daily challenges, and climb a live leaderboard — all built with Django.

---

## Project Structure

```
codez_final/
├── manage.py
├── requirements.txt
├── codez_project/          ← Django project config (settings, root URLs, WSGI)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── codez/                  ← The single Django app
    ├── models.py           ← All database models
    ├── views.py            ← All view functions
    ├── urls.py             ← All URL patterns
    ├── admin.py            ← Admin panel configuration
    ├── signals.py          ← Signal handlers (auto-profile, notifications, badges)
    ├── apps.py
    ├── migrations/         ← Three migration files (0001 → 0003)
    ├── templates/codez/    ← All 18 HTML templates
    └── management/
        └── commands/
            └── seed_data.py  ← Developer data seeder
```

---

## Quick Start (Step-by-Step)

### Step 1 — Create and activate a virtual environment

```bash
python -m venv venv

# On macOS / Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Apply all database migrations

This creates the SQLite database (`db.sqlite3`) and all tables:

```bash
python manage.py migrate
```

You should see output confirming migrations 0001, 0002, and 0003 all applied.

### Step 4 — Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password. You'll use this
to log in at `/admin/` and to test the app.

### Step 5 — Seed sample data (recommended for development)

This command creates 10 sample users, 30 questions, answers, votes, follows,
learning paths, and a daily challenge so the app feels alive immediately:

```bash
python manage.py seed_data
```

Options if you want more content:

```bash
python manage.py seed_data --users 20 --questions 60
```

All seeded users have the password `password123`.

### Step 6 — Start the development server

```bash
python manage.py runserver
```

Then open your browser:

- **App:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

---

## Features

### Core (always available)

**Authentication** — Register, log in, and log out. A `UserProfile` is
automatically created via Django signals the moment a new user registers. The
daily login streak is updated on every successful login.

**Home Feed** — A paginated list of all questions, sortable by "New", "Top"
(by votes), or "Hot" (by answer count + views). Filterable by difficulty,
language, and tag.

**Question Detail** — Full question page with all answers ranked by acceptance
then vote score. AJAX upvote/downvote buttons update counts without a page
reload. The question author can accept any answer.

**Voting** — Users can upvote or downvote questions and answers. Voting the
same direction a second time removes the vote (toggle). Signals automatically
award points to authors when their content is upvoted.

**Bookmarks** — Save any question and view all saved questions at `/bookmarks/`.

**Search** — Full-text search across question titles, bodies, tags, and
usernames.

**Leaderboard** — Three tabs: Global (all time), Weekly (active in last 7
days), and Friends (users you follow). Users can opt out via privacy settings.

**Notifications** — Automatically generated for upvotes, new answers, follows,
badge earnings, and accepted answers. Unread count shown in the nav bar and
updated every 60 seconds via a polling API call.

**Follow System** — Follow/unfollow any user. Generates a notification for
the target user.

**Profile** — Public profile page showing stats (points, XP, level, streak,
accuracy), badges earned, recent questions, answers, and bookmarks.

**Settings** — Users can update their profile info, change their password,
control notification preferences, set privacy options (hide from leaderboard,
private profile), and switch between light and dark themes.

### Feature 1 — Learning Paths (`/learn/`)

Curated sequences of questions organised by language and level (Beginner /
Intermediate / Pro). Users enrol automatically when they visit a path, and
can mark each step complete for 10 points + 15 XP. A progress bar tracks
completion percentage.

### Feature 2 — Daily Challenge (`/daily/`)

One question is featured each day with bonus points (20–30). Completing the
challenge also triggers a streak update. Admins assign daily challenges through
the admin panel.

### Feature 3 — Project Forum (`/projects/`)

Users share their own coding projects with a title, description, code snippet,
repo link, and demo link. Others can upvote projects and leave feedback
(optionally flagging it as a bug report for a 10-point bonus to the reporter).

### Feature 4 — Doubt Forum (`/doubts/`)

A dedicated space for asking about specific questions. Threads are linked to
a Question. Replies can be upvoted and the thread author can mark one reply as
the accepted answer, which resolves the thread and awards the replier 10 points.

### Gamification System

Every user has points, XP, a level, and a streak. Points are awarded for
answering, accepting, voting, completing learning steps, finishing daily
challenges, and reporting bugs. XP feeds a level-up system (every `level × 200`
XP earns a new level). Seven badge types are automatically awarded when
milestones are reached (First Solve, 7-Day Streak, 30-Day Streak, 100/500/1000
Points, Top 10 Rank).

---

## Admin Panel

Visit `/admin/` and log in with your superuser. Every model is registered with
sensible `list_display`, `list_filter`, `search_fields`, and where relevant
inline editors. You can:

- Manage all users and their profiles.
- Create, edit, and delete questions, answers, and tags.
- Set the daily challenge question for any date.
- Create and populate learning paths with step ordering.
- Monitor notifications and mark them read in bulk.
- Award or revoke badges from users.

---

## Settings Reference

The project settings live at `codez_project/settings.py`. Key values to change
before deploying to production:

| Setting | Default | What to change |
|---|---|---|
| `SECRET_KEY` | Insecure placeholder | Set from environment variable |
| `DEBUG` | `True` | Set to `False` |
| `ALLOWED_HOSTS` | `['*']` | Set to your domain |
| `DATABASES` | SQLite | Switch to PostgreSQL |

---

## URL Map (All Endpoints)

```
/                          Home feed
/login/                    Login
/register/                 Register
/logout/                   Logout

/profile/                  My profile
/profile/<username>/       Another user's profile
/follow/<username>/        Follow/unfollow (POST, AJAX)

/question/                 Latest question
/question/<pk>/            Question detail
/question/<pk>/answer/     Submit answer (POST)
/answer/<pk>/accept/       Accept answer (POST)

/search/                   Search
/bookmarks/                My saved questions
/leaderboard/              Leaderboard (tabs: global/weekly/friends)
/settings/                 Account settings
/notifications/            Notification list

/learn/                    Learning paths list
/learn/<pk>/               Learning path detail
/daily/                    Daily challenge

/projects/                 Project forum
/projects/<pk>/            Project detail
/projects/submit/          Submit a project

/doubts/                   Doubt forum
/doubts/new/               Post a doubt thread (POST)
/doubts/<pk>/              Doubt thread detail
/doubts/<pk>/reply/        Post a reply (POST)

/api/vote/question/<pk>/   Vote on question (AJAX POST)
/api/vote/answer/<pk>/     Vote on answer (AJAX POST)
/api/bookmark/<pk>/        Toggle bookmark (AJAX POST)
/api/notif/count/          Unread notification count (AJAX GET)
/api/notif/<pk>/read/      Mark notification read (AJAX POST)
/api/learn/step/<pk>/done/ Complete a learning step (AJAX POST)
/api/projects/<pk>/upvote/ Toggle project upvote (AJAX POST)
/api/projects/<pk>/feedback/  Submit project feedback (POST)
/api/feedback/<pk>/upvote/ Upvote feedback (AJAX POST)

## Authors
- [LOHITH A.S](https://github.com/mr-lohith)
- [ARYAN JAYAN MENON ](https://github.com/aryanjm1405)
- [SOURAV SURESH](https://github.com/souravofficialx)


