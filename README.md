# API Fusion — Ideathon Wheel App

A Django + HTML5 Canvas + Vanilla JS app for the "API Fusion" ideathon.
Teams register, log in, spin a wheel twice to get two random public APIs,
then get permanently locked. Admins track everything from Django Admin.

## File Structure

```
api_fusion/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
├── api_fusion/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── teams/
    ├── __init__.py
    ├── apps.py
    ├── models.py        # TeamProfile model + API_POOL
    ├── forms.py          # TeamRegistrationForm
    ├── admin.py           # TeamProfileAdmin + CSV export
    ├── views.py            # register/login/wheel/spin views
    ├── urls.py
    ├── migrations/
    │   └── __init__.py
    ├── templates/teams/
    │   ├── base.html
    │   ├── register.html
    │   ├── login.html
    │   └── wheel.html       # canvas wheel + locked dashboard
    └── static/teams/
        ├── css/style.css
        └── js/wheel.js       # Canvas wheel + AJAX /spin/ calls
```

## Local Setup

```bash
cd api_fusion
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY etc.

python manage.py makemigrations teams
python manage.py migrate

python manage.py createsuperuser   # for /admin/ access

python manage.py runserver
```

Visit `http://127.0.0.1:8000/register/` to create a team, then
`http://127.0.0.1:8000/wheel/` to spin. Visit `/admin/` to see the
live tracking dashboard.

## How the locking logic works

- `TeamProfile.spin_count` starts at 0, `is_locked` starts False.
- Every click of **SPIN** calls `POST /spin/`. The **server** (not the
  browser) picks the random API from the 16-item pool, skipping any
  API already assigned to that team, and saves it to `api_1` (1st
  spin) or `api_2` (2nd spin).
- After the 2nd spin, `is_locked` is set `True` and the view starts
  returning `400` for any further spin attempts, regardless of what
  the client sends.
- The `wheel.html` template checks `profile.is_locked` /
  `profile.spin_count` server-side on every page load, so a locked
  team always sees the read-only "Your Assigned APIs" dashboard even
  if they refresh, reopen the page, or try to hit `/spin/` directly.

## Admin Dashboard

Go to `/admin/` and log in with your superuser. The **Team Profiles**
section shows Team Name, Spin Count, API 1, API 2, Is Locked, with:
- Search by team name / leader contact
- Filter sidebar by `is_locked` and `spin_count`
- Select rows → **Actions → "Export selected teams to CSV"** to
  download all allocations as a `.csv` file.

## Deploying to Render (Free Tier)

1. **Push this project to a GitHub repository.**

2. **Create a Postgres database on Render**
   - Render Dashboard → New → PostgreSQL → pick the free plan.
   - Copy the **Internal Database URL** once it's provisioned.

3. **Create a Web Service on Render**
   - Render Dashboard → New → Web Service → connect your GitHub repo.
   - **Runtime**: Python 3
   - **Build Command**:
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```
     gunicorn api_fusion.wsgi:application
     ```
   - Render automatically detects the `Procfile`, but setting the
     Start Command explicitly also works if you skip the Procfile.

4. **Set Environment Variables** on the Web Service (Settings → Environment):
   | Key | Value |
   |---|---|
   | `SECRET_KEY` | a long random string |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
   | `DATABASE_URL` | the Internal Database URL from step 2 |
   | `SECURE_SSL_REDIRECT` | `True` |

5. **Deploy.** Render will build, run `python manage.py migrate`
   automatically via the `release` line in the `Procfile`, then start
   gunicorn.

6. **Create an admin user** — open the Render **Shell** tab for the
   web service and run:
   ```
   python manage.py createsuperuser
   ```

7. Visit `https://your-app-name.onrender.com/register/` to confirm
   it's live, and `/admin/` for the tracking dashboard.

### Deploying to Railway instead

The steps are almost identical:
1. New Project → Deploy from GitHub repo.
2. Add a **PostgreSQL** plugin; Railway auto-injects `DATABASE_URL`.
3. Add the same environment variables as above (`SECRET_KEY`,
   `DEBUG=False`, `ALLOWED_HOSTS=<your-app>.up.railway.app`).
4. Railway reads the `Procfile` automatically and runs the `release`
   and `web` commands the same way Render does.
5. Use the Railway Shell (or a one-off command) to run
   `python manage.py createsuperuser`.

## Notes

- WhiteNoise serves `/static/` files directly from the Django process
  in production — no separate static file host needed.
- SQLite is used automatically for local dev if `DATABASE_URL` is
  unset; Postgres is used automatically once `DATABASE_URL` is set in
  production.
- The 16-API pool lives in `teams/models.py` as `API_POOL` — edit that
  list if you need to swap APIs in/out before the event.
