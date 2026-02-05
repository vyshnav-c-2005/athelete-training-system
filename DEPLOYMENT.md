# Deployment Guide

This project is ready for deployment on platforms like Render, Railway, or PythonAnywhere.

## 1. Pre-Deployment Configuration (Checklist)

- [ ] **DEBUG**: Set `DEBUG = False` in `settings.py` (use environment variables).
- [ ] **SECRET_KEY**: Do NOT hardcode in production. Use `os.environ.get('SECRET_KEY')`.
- [ ] **ALLOWED_HOSTS**: Add your production domain (e.g., `['myapp.onrender.com']`).
- [ ] **Static Files**: Ensure `STATIC_ROOT` is set (Done). Run `python manage.py collectstatic`.

## 2. Platform-Specific Instructions

### Option A: Render (Recommended)
1. **Create Web Service**: Connect your GitHub repo.
2. **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
3. **Start Command**: `gunicorn athlete_ai_system.wsgi:application`
4. **Environment Variables**: Add `PYTHON_VERSION` (e.g., 3.9.0), `SECRET_KEY`, `WEB_CONCURRENCY` (e.g. 4).

### Option B: PythonAnywhere
1. **Upload Code** or git clone.
2. **Virtualenv**: Create via dashboard console `mkvirtualenv --python=/usr/bin/python3.10 myenv`.
3. **WSGI Config**: Edit the WSGI configuration file to point to your project path.
4. **Static Files**: Map `/static/` to `/home/youruser/project02/staticfiles` in the "Web" tab.

## 3. Common Pitfalls
- **Database**: This project uses SQLite by default. For production (Render/Railway), data persists only on persistent disks. It is recommended to switch to **PostgreSQL** by updating `DATABASES` in `settings.py` and installing `psycopg2-binary`.
- **Static Files**: If CSS is missing, ensure `collectstatic` ran and your web server is configured to serve the `staticfiles` directory.
- **CSRF Errors**: Ensure `CSRF_TRUSTED_ORIGINS` includes your domain (requires Django 4.0+ config update).

## 4. Requirements
Ensure `gunicorn` is in your `requirements.txt` if using Render/Railway.
```bash
pip install gunicorn
pip freeze > requirements.txt
```
