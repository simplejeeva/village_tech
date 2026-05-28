# Village Tech

Colorful, mobile-first Django landing page + customer registration for the
**Village Tech** doorstep delivery business (groceries, meat, vegetables).

## Run locally (Windows PowerShell)

```powershell
# one-time setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env       # then edit .env and set DJANGO_SECRET_KEY
python manage.py migrate
python manage.py createsuperuser  # for /admin/

# run the dev server
python manage.py runserver
```

Then open:
- `http://127.0.0.1:8000/` — the landing page
- `http://127.0.0.1:8000/admin/` — admin (use the superuser you created)

## Run tests

```powershell
python manage.py test customers -v 2
```

## Project layout

- `village_tech/` — Django project settings & root URLs
- `customers/` — the single app: model, form, views, admin
- `templates/` — `base.html`, `landing.html`, `thank_you.html`
- `static/css/styles.css` — brand palette and custom styles

## Brand contact

- Phone: 9600877537
- WhatsApp: https://wa.me/919600877537
