# Village Tech — Landing Page & Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **No git for this project.** Per user instruction, do NOT run any `git` commands. The plan template normally includes commit steps after each task; for this project those are intentionally omitted. Save files, run tests, move on.

**Goal:** Build a colorful, mobile-first Django website for **Village Tech** doorstep delivery — one landing page that tells the brand story plus an inline registration form whose entries land in Django admin.

**Architecture:** A single Django project (`village_tech`) with one app (`customers`). Server-rendered HTML with Bootstrap 5 from CDN. One `Customer` model storing name / phone / place / notes / contacted / created_at. Three URLs: `/` (landing with inline form), `/register/` (POST handler, also accepts GET), `/thank-you/` (post-submit confirmation). Django's built-in admin at `/admin/`.

**Tech Stack:** Python 3.11+, Django 5, SQLite (default), Bootstrap 5 (CDN), Whitenoise, python-dotenv. Tests use Django's built-in test runner.

**Approved spec:** `docs/superpowers/specs/2026-05-28-village-tech-landing-and-register-design.md`

**Working directory:** `C:\Users\jeeva\OneDrive\Desktop\delivery` (all relative paths below are from this root). **Shell:** PowerShell on Windows.

---

## File Structure (target end-state)

```
delivery/
├── .env.example                    # template for SECRET_KEY (real .env not tracked)
├── .gitignore                      # courtesy file; we don't use git but IDEs read it
├── manage.py                       # Django entry point
├── requirements.txt                # pinned dependencies
├── README.md                       # how to run locally
├── db.sqlite3                      # auto-generated, do not edit
├── village_tech/                   # project package
│   ├── __init__.py
│   ├── settings.py                 # all config
│   ├── urls.py                     # root URL conf
│   ├── wsgi.py
│   └── asgi.py
├── customers/                      # the only app
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                   # Customer model
│   ├── admin.py                    # admin config
│   ├── forms.py                    # CustomerForm with validation
│   ├── views.py                    # landing, register, thank_you
│   ├── urls.py                     # customers app URL conf
│   ├── tests.py                    # model, form, view tests
│   └── migrations/
│       └── __init__.py
├── templates/                      # project-level templates
│   ├── base.html                   # layout + Bootstrap + brand colors
│   ├── landing.html                # the colorful page
│   └── thank_you.html              # confirmation
└── static/
    └── css/
        └── styles.css              # brand palette, hero, cards
```

**Responsibility per file (one purpose each):**
- `models.py` — data only, no business logic beyond the model `__str__` and Meta.
- `forms.py` — input validation (phone normalization, soft dedupe lookup).
- `views.py` — request → form → response wiring. No HTML strings; templates only.
- `admin.py` — admin display, search, filters, custom action.
- `urls.py` — routes only.
- `templates/landing.html` — extends base, contains all marketing sections + inline form.
- `templates/thank_you.html` — confirmation only.
- `static/css/styles.css` — brand colors + custom overrides on top of Bootstrap.

---

## Task 1: Bootstrap the Django project

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `manage.py` (via `django-admin startproject`)
- Create: `village_tech/settings.py` (and siblings)

- [ ] **Step 1: Open a PowerShell terminal in the project root**

Run: `Set-Location "C:\Users\jeeva\OneDrive\Desktop\delivery"`

Expected: prompt now shows the `delivery` directory.

- [ ] **Step 2: Create and activate a virtual environment**

Run:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation with "running scripts is disabled", run once:
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
then re-run the activation command.

Expected: prompt prefixed with `(.venv)`.

- [ ] **Step 3: Create `requirements.txt`**

Write this exact content to `requirements.txt`:
```
Django>=5.0,<6.0
whitenoise>=6.6
python-dotenv>=1.0
```

- [ ] **Step 4: Install dependencies**

Run: `pip install -r requirements.txt`

Expected: Django, whitenoise, python-dotenv installed without errors.

- [ ] **Step 5: Generate the Django project skeleton in the current folder**

Run: `django-admin startproject village_tech .`

(The trailing dot puts `manage.py` directly in the cwd instead of nesting a folder.)

Expected: `manage.py` and `village_tech/` now exist.

- [ ] **Step 6: Create `.env.example`**

Write this exact content to `.env.example`:
```
# Copy this file to .env and fill the values.
DJANGO_SECRET_KEY=replace-me-with-a-long-random-string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

- [ ] **Step 7: Create `.gitignore`** (courtesy file for IDEs; we do not use git in this project)

Write this exact content to `.gitignore`:
```
.venv/
__pycache__/
*.pyc
db.sqlite3
.env
.idea/
.vscode/
```

- [ ] **Step 8: Create a real local `.env`** (this file stays on disk only, never shared)

Copy `.env.example` to `.env` and replace the placeholder secret key with any long random string (e.g. press a-z keys for ~50 chars). Set `DJANGO_DEBUG=True` for development.

PowerShell:
```powershell
Copy-Item .env.example .env
```
Then open `.env` in your editor and edit `DJANGO_SECRET_KEY`.

- [ ] **Step 9: Replace `village_tech/settings.py` so it reads from `.env`, adds Whitenoise, and points at the project-level `templates/` and `static/` folders**

Open `village_tech/settings.py` and replace its **entire contents** with the block below:

```python
"""Django settings for Village Tech."""
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # local
    "customers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "village_tech.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "village_tech.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Brand info — surfaced in templates via a context processor in a later task.
VILLAGE_TECH_PHONE = "9600877537"
VILLAGE_TECH_BRAND = "Village Tech"
```

- [ ] **Step 10: Create empty `templates/` and `static/css/` directories so settings paths exist**

PowerShell:
```powershell
New-Item -ItemType Directory -Force -Path templates | Out-Null
New-Item -ItemType Directory -Force -Path static\css | Out-Null
```

- [ ] **Step 11: Verify the project starts**

Run: `python manage.py check`

Expected output: `System check identified no issues (0 silenced).`

- [ ] **Step 12: Run the dev server briefly to confirm it boots**

Run: `python manage.py runserver`

Expected: server starts on `http://127.0.0.1:8000/`. Open the URL — you'll see Django's default landing page (we'll replace it in Task 7). Stop the server with `Ctrl+C`.

---

## Task 2: Create the `customers` app

**Files:**
- Create: `customers/` (via `startapp`)
- Modify: `customers/apps.py`
- Verify: `customers` already in `INSTALLED_APPS` (from Task 1)

- [ ] **Step 1: Create the app**

Run: `python manage.py startapp customers`

Expected: `customers/` directory with default skeleton (`models.py`, `views.py`, `admin.py`, etc.).

- [ ] **Step 2: Update `customers/apps.py` with a friendly verbose name**

Replace the contents of `customers/apps.py` with:
```python
from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customers"
    verbose_name = "Customer Registrations"
```

- [ ] **Step 3: Verify the app loads**

Run: `python manage.py check`

Expected: `System check identified no issues (0 silenced).`

---

## Task 3: `Customer` model (TDD)

**Files:**
- Modify: `customers/models.py`
- Modify: `customers/tests.py`
- Create: `customers/migrations/0001_initial.py` (auto-generated)

- [ ] **Step 1: Write the failing model tests**

Replace the contents of `customers/tests.py` with:
```python
from django.test import TestCase

from customers.models import Customer


class CustomerModelTests(TestCase):
    def test_str_contains_name_phone_and_place(self):
        customer = Customer.objects.create(
            name="Anbu",
            phone="9600012345",
            place="T. Nagar",
        )
        self.assertIn("Anbu", str(customer))
        self.assertIn("9600012345", str(customer))
        self.assertIn("T. Nagar", str(customer))

    def test_contacted_defaults_to_false(self):
        customer = Customer.objects.create(
            name="Anbu", phone="9600012345", place="T. Nagar"
        )
        self.assertFalse(customer.contacted)

    def test_notes_optional(self):
        customer = Customer.objects.create(
            name="Anbu", phone="9600012345", place="T. Nagar"
        )
        self.assertEqual(customer.notes, "")

    def test_ordering_is_newest_first(self):
        older = Customer.objects.create(
            name="A", phone="9600000001", place="X"
        )
        newer = Customer.objects.create(
            name="B", phone="9600000002", place="Y"
        )
        self.assertEqual(list(Customer.objects.all()), [newer, older])
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python manage.py test customers -v 2`

Expected: tests **fail** with `ImportError: cannot import name 'Customer'` (or similar) — the model does not exist yet.

- [ ] **Step 3: Implement the `Customer` model**

Replace the contents of `customers/models.py` with:
```python
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=15, db_index=True)
    place = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self) -> str:
        return f"{self.name} ({self.phone}) — {self.place}"
```

- [ ] **Step 4: Generate the migration**

Run: `python manage.py makemigrations customers`

Expected: `Migrations for 'customers': 0001_initial.py`.

- [ ] **Step 5: Apply migrations**

Run: `python manage.py migrate`

Expected: all migrations applied including `customers.0001_initial`.

- [ ] **Step 6: Run the tests and verify they pass**

Run: `python manage.py test customers -v 2`

Expected: `Ran 4 tests` — all pass.

---

## Task 4: Admin configuration

**Files:**
- Modify: `customers/admin.py`
- Modify: `customers/tests.py` (append tests)

- [ ] **Step 1: Append admin tests to `customers/tests.py`**

Add this class to the bottom of `customers/tests.py` (keep the existing test class):
```python
from django.contrib import admin as django_admin

from customers.admin import CustomerAdmin
from customers.models import Customer as _CustomerForAdminTest


class CustomerAdminTests(TestCase):
    def test_customer_registered_with_admin(self):
        self.assertIn(_CustomerForAdminTest, django_admin.site._registry)

    def test_list_display_fields(self):
        for field in ("name", "phone", "place", "contacted", "created_at"):
            self.assertIn(field, CustomerAdmin.list_display)

    def test_search_fields(self):
        for field in ("name", "phone", "place"):
            self.assertIn(field, CustomerAdmin.search_fields)

    def test_mark_contacted_action_present(self):
        self.assertIn("mark_as_contacted", [a.__name__ for a in CustomerAdmin.actions])
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python manage.py test customers.tests.CustomerAdminTests -v 2`

Expected: failure — `CustomerAdmin` does not exist yet.

- [ ] **Step 3: Implement `customers/admin.py`**

Replace the contents of `customers/admin.py` with:
```python
from django.contrib import admin

from customers.models import Customer


def mark_as_contacted(modeladmin, request, queryset):
    queryset.update(contacted=True)


mark_as_contacted.short_description = "Mark selected as contacted"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "place", "contacted", "created_at")
    list_filter = ("contacted", "created_at")
    search_fields = ("name", "phone", "place")
    list_editable = ("contacted",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = [mark_as_contacted]
    readonly_fields = ("created_at",)
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python manage.py test customers -v 2`

Expected: all tests pass (8 so far).

- [ ] **Step 5: Create a superuser so you can log into `/admin/` later**

Run: `python manage.py createsuperuser`

Pick a username, leave email blank if you like, set a password. You'll use this at `/admin/`.

- [ ] **Step 6: Smoke-test the admin manually**

Run: `python manage.py runserver`
Open `http://127.0.0.1:8000/admin/`, log in, click **Customers**. The list should be empty but reachable. Stop the server with `Ctrl+C`.

---

## Task 5: `CustomerForm` with validation and soft dedupe (TDD)

**Files:**
- Create: `customers/forms.py`
- Modify: `customers/tests.py` (append tests)

- [ ] **Step 1: Append form tests to `customers/tests.py`**

Add this class to the bottom of `customers/tests.py`:
```python
from datetime import timedelta
from django.utils import timezone

from customers.forms import CustomerForm


class CustomerFormTests(TestCase):
    valid_data = {
        "name": "Anbu",
        "phone": "9600012345",
        "place": "T. Nagar",
        "notes": "rice, dal, chicken",
    }

    def test_valid_form_saves_customer(self):
        form = CustomerForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        customer = form.save()
        self.assertEqual(customer.name, "Anbu")
        self.assertEqual(customer.phone, "9600012345")
        self.assertEqual(customer.place, "T. Nagar")
        self.assertEqual(customer.notes, "rice, dal, chicken")

    def test_phone_with_spaces_and_dashes_is_normalized(self):
        form = CustomerForm(
            data={**self.valid_data, "phone": "96000-12345"}
        )
        self.assertTrue(form.is_valid(), form.errors)
        customer = form.save()
        self.assertEqual(customer.phone, "9600012345")

    def test_phone_with_country_code_is_normalized(self):
        form = CustomerForm(
            data={**self.valid_data, "phone": "+91 96000 12345"}
        )
        self.assertTrue(form.is_valid(), form.errors)
        customer = form.save()
        self.assertEqual(customer.phone, "9600012345")

    def test_phone_too_short_rejected(self):
        form = CustomerForm(data={**self.valid_data, "phone": "12345"})
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_phone_too_long_rejected(self):
        form = CustomerForm(data={**self.valid_data, "phone": "123456789012"})
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_missing_name_rejected(self):
        form = CustomerForm(data={**self.valid_data, "name": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_missing_place_rejected(self):
        form = CustomerForm(data={**self.valid_data, "place": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("place", form.errors)

    def test_notes_optional(self):
        form = CustomerForm(data={**self.valid_data, "notes": ""})
        self.assertTrue(form.is_valid(), form.errors)
        customer = form.save()
        self.assertEqual(customer.notes, "")

    def test_soft_dedupe_within_60_seconds_returns_existing(self):
        first = Customer.objects.create(
            name="Anbu", phone="9600012345", place="T. Nagar"
        )
        form = CustomerForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.pk, first.pk)
        self.assertEqual(Customer.objects.count(), 1)

    def test_dedupe_window_expires_after_60_seconds(self):
        first = Customer.objects.create(
            name="Anbu", phone="9600012345", place="T. Nagar"
        )
        # Backdate by 2 minutes
        Customer.objects.filter(pk=first.pk).update(
            created_at=timezone.now() - timedelta(minutes=2)
        )
        form = CustomerForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)
        second = form.save()
        self.assertNotEqual(second.pk, first.pk)
        self.assertEqual(Customer.objects.count(), 2)
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python manage.py test customers.tests.CustomerFormTests -v 2`

Expected: import error — `customers.forms` does not exist.

- [ ] **Step 3: Implement `customers/forms.py`**

Create `customers/forms.py` with this exact content:
```python
import re
from datetime import timedelta

from django import forms
from django.utils import timezone

from customers.models import Customer

DEDUPE_WINDOW = timedelta(seconds=60)
_NON_DIGIT = re.compile(r"\D+")


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "phone", "place", "notes")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Your name",
                    "autocomplete": "name",
                    "required": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "10-digit mobile number",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "required": True,
                }
            ),
            "place": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Your area / locality",
                    "autocomplete": "address-level2",
                    "required": True,
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "What do you usually buy? (optional)",
                    "rows": 3,
                    "maxlength": 500,
                }
            ),
        }
        labels = {
            "name": "Name",
            "phone": "Phone",
            "place": "Place / Area",
            "notes": "What you usually buy",
        }

    def clean_name(self) -> str:
        value = (self.cleaned_data.get("name") or "").strip()
        if not value:
            raise forms.ValidationError("Please enter your name.")
        return value

    def clean_place(self) -> str:
        value = (self.cleaned_data.get("place") or "").strip()
        if not value:
            raise forms.ValidationError("Please tell us your area.")
        return value

    def clean_phone(self) -> str:
        raw = self.cleaned_data.get("phone") or ""
        digits = _NON_DIGIT.sub("", raw)
        # Drop a leading country code "91" if present and length is 12
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        if len(digits) != 10:
            raise forms.ValidationError(
                "Please enter a valid 10-digit mobile number."
            )
        return digits

    def save(self, commit: bool = True) -> Customer:
        # Soft dedupe: if a row with same phone + place exists within the last
        # 60 seconds, return that one instead of creating a duplicate.
        phone = self.cleaned_data["phone"]
        place = self.cleaned_data["place"]
        cutoff = timezone.now() - DEDUPE_WINDOW
        existing = (
            Customer.objects.filter(
                phone=phone, place=place, created_at__gte=cutoff
            )
            .order_by("-created_at")
            .first()
        )
        if existing is not None:
            return existing
        return super().save(commit=commit)
```

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python manage.py test customers -v 2`

Expected: all 17 tests pass.

---

## Task 6: URLs, views, and the `phone_mask` helper (TDD)

**Files:**
- Create: `customers/urls.py`
- Modify: `customers/views.py`
- Modify: `village_tech/urls.py`
- Create: stub templates at `templates/landing.html` and `templates/thank_you.html` (placeholder content — proper templates land in Tasks 8–10)
- Modify: `customers/tests.py` (append tests)

- [ ] **Step 1: Append view tests to `customers/tests.py`**

Add this class to the bottom of `customers/tests.py`:
```python
from django.urls import reverse


class CustomerViewTests(TestCase):
    def test_landing_returns_200(self):
        response = self.client.get(reverse("customers:landing"))
        self.assertEqual(response.status_code, 200)

    def test_landing_contains_brand(self):
        response = self.client.get(reverse("customers:landing"))
        self.assertContains(response, "Village Tech")

    def test_register_post_valid_redirects_to_thank_you(self):
        response = self.client.post(
            reverse("customers:register"),
            data={
                "name": "Anbu",
                "phone": "9600012345",
                "place": "T. Nagar",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("customers:thank_you"), response.url)
        self.assertEqual(Customer.objects.count(), 1)

    def test_register_post_invalid_rerenders_landing(self):
        response = self.client.post(
            reverse("customers:register"),
            data={"name": "", "phone": "123", "place": "", "notes": ""},
        )
        self.assertEqual(response.status_code, 200)
        # form rendered with errors → still on landing template
        self.assertContains(response, "Village Tech")
        self.assertEqual(Customer.objects.count(), 0)

    def test_thank_you_masks_phone(self):
        response = self.client.get(
            reverse("customers:thank_you") + "?phone=9600012345"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "96000-XXXXX")
        # Full phone must NOT leak
        self.assertNotContains(response, "9600012345")

    def test_thank_you_without_phone_param_still_renders(self):
        response = self.client.get(reverse("customers:thank_you"))
        self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python manage.py test customers.tests.CustomerViewTests -v 2`

Expected: failures — URL names `customers:landing`, `customers:register`, `customers:thank_you` are not registered yet.

- [ ] **Step 3: Create `customers/urls.py`**

Create `customers/urls.py` with this exact content:
```python
from django.urls import path

from customers import views

app_name = "customers"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("thank-you/", views.thank_you, name="thank_you"),
]
```

- [ ] **Step 4: Wire the customers URLs into the project**

Replace the contents of `village_tech/urls.py` with:
```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("customers.urls", namespace="customers")),
]
```

- [ ] **Step 5: Implement `customers/views.py`**

Replace the contents of `customers/views.py` with:
```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from customers.forms import CustomerForm


def _mask_phone(raw: str | None) -> str:
    """Return the phone with its last 5 digits hidden, e.g. '96000-XXXXX'.

    Falls back to a generic placeholder if the input is missing or malformed.
    """
    digits = "".join(ch for ch in (raw or "") if ch.isdigit())
    if len(digits) != 10:
        return "your number"
    return f"{digits[:5]}-XXXXX"


@require_http_methods(["GET", "POST"])
def landing(request: HttpRequest) -> HttpResponse:
    form = CustomerForm()
    return render(request, "landing.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect(
                f"{reverse('customers:thank_you')}?phone={customer.phone}"
            )
        # invalid → re-render landing with the bound form so errors show
        return render(
            request,
            "landing.html",
            {"form": form, "scroll_to_form": True},
            status=200,
        )
    # GET on /register/ just shows the landing form
    return redirect("customers:landing")


@require_http_methods(["GET"])
def thank_you(request: HttpRequest) -> HttpResponse:
    masked = _mask_phone(request.GET.get("phone"))
    return render(request, "thank_you.html", {"masked_phone": masked})
```

- [ ] **Step 6: Create stub templates so the views can render during tests**

Create `templates/landing.html` with this stub content (a real template lands in Tasks 8–10):
```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Village Tech</title></head>
<body>
<h1>Village Tech</h1>
<form method="post" action="{% url 'customers:register' %}">{% csrf_token %}
{{ form.as_p }}
<button type="submit">Register</button>
</form>
</body></html>
```

Create `templates/thank_you.html` with this stub content:
```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Thank you — Village Tech</title></head>
<body>
<h1>Thank you!</h1>
<p>We will call you soon at {{ masked_phone }}.</p>
<a href="{% url 'customers:landing' %}">Back to home</a>
</body></html>
```

- [ ] **Step 7: Run all tests and verify they pass**

Run: `python manage.py test customers -v 2`

Expected: all tests pass (23 total).

- [ ] **Step 8: Smoke-test in the browser**

Run: `python manage.py runserver`
- Open `http://127.0.0.1:8000/` — stub landing renders.
- Fill the form with `Name=Anbu`, `Phone=9600012345`, `Place=T. Nagar`, submit.
- You should land on `/thank-you/?phone=9600012345` showing **96000-XXXXX**.
- Open `http://127.0.0.1:8000/admin/`, log in, click **Customers** — the new row should be there.
- Stop the server.

---

## Task 7: Brand context processor and Bootstrap-ready `base.html`

**Files:**
- Create: `customers/context_processors.py`
- Modify: `village_tech/settings.py` (add the context processor)
- Modify: `templates/base.html` (replace stub)

- [ ] **Step 1: Create the context processor**

Create `customers/context_processors.py` with this exact content:
```python
from django.conf import settings


def brand(request):
    return {
        "brand_name": getattr(settings, "VILLAGE_TECH_BRAND", "Village Tech"),
        "brand_phone": getattr(settings, "VILLAGE_TECH_PHONE", ""),
    }
```

- [ ] **Step 2: Register the context processor in settings**

In `village_tech/settings.py`, find the `TEMPLATES` list and add `"customers.context_processors.brand"` to the `context_processors` list. The list should look like:
```python
"context_processors": [
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "customers.context_processors.brand",
],
```

- [ ] **Step 3: Create `templates/base.html` with Bootstrap, Google Fonts, and brand colors**

Replace the contents of `templates/base.html` (create it if it does not exist) with:
```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{{ brand_name }} — fresh groceries, meat & vegetables delivered to your doorstep.">
  <title>{% block title %}{{ brand_name }} — Doorstep Delivery{% endblock %}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{% static 'css/styles.css' %}" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-expand-lg vt-navbar sticky-top">
    <div class="container">
      <a class="navbar-brand fw-bold" href="{% url 'customers:landing' %}">
        <span class="vt-leaf">🌿</span> {{ brand_name }}
      </a>
      <div class="d-flex align-items-center gap-2">
        <a class="btn btn-sm vt-btn-outline d-none d-sm-inline-flex" href="tel:{{ brand_phone }}">
          📞 {{ brand_phone }}
        </a>
        <a class="btn btn-sm vt-btn-primary" href="#register">Register</a>
      </div>
    </div>
  </nav>

  {% block content %}{% endblock %}

  <footer class="vt-footer">
    <div class="container py-4 text-center">
      <p class="mb-1"><strong>{{ brand_name }}</strong> — fresh to your doorstep</p>
      <p class="mb-1">
        📞 <a href="tel:{{ brand_phone }}">{{ brand_phone }}</a>
        &nbsp;·&nbsp;
        <a href="https://wa.me/91{{ brand_phone }}" target="_blank" rel="noopener">WhatsApp</a>
      </p>
      <p class="small text-muted mb-0">&copy; {{ brand_name }}</p>
    </div>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Step 4: Replace `static/css/styles.css` with the brand palette and base styles**

Create / replace `static/css/styles.css` with:
```css
:root {
  --vt-green: #2E7D32;
  --vt-green-dark: #1B5E20;
  --vt-orange: #FB8C00;
  --vt-yellow: #FFC107;
  --vt-cream: #FFF8E1;
  --vt-text: #212121;
}

* { box-sizing: border-box; }

html, body {
  background: var(--vt-cream);
  color: var(--vt-text);
  font-family: "Poppins", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  margin: 0;
}

h1, h2, h3, h4 { font-weight: 700; line-height: 1.2; }
h1 { font-size: clamp(1.8rem, 6vw, 3rem); }
h2 { font-size: clamp(1.4rem, 4.5vw, 2.2rem); }

a { color: var(--vt-green-dark); }
a:hover { color: var(--vt-orange); }

.vt-navbar {
  background: #ffffffd9;
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #00000010;
}
.vt-navbar .navbar-brand { color: var(--vt-green-dark); font-size: 1.25rem; }
.vt-leaf { font-size: 1.3rem; }

.vt-btn-primary {
  background: var(--vt-green);
  color: #fff;
  border: 0;
  padding: 0.55rem 1.1rem;
  border-radius: 999px;
  font-weight: 600;
}
.vt-btn-primary:hover { background: var(--vt-orange); color: #fff; }

.vt-btn-outline {
  background: transparent;
  color: var(--vt-green-dark);
  border: 1.5px solid var(--vt-green);
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  font-weight: 600;
}
.vt-btn-outline:hover { background: var(--vt-green); color: #fff; }

.vt-footer {
  background: var(--vt-green-dark);
  color: #fff;
}
.vt-footer a { color: var(--vt-yellow); text-decoration: none; }
.vt-footer a:hover { color: #fff; }
```

- [ ] **Step 5: Run tests to make sure nothing broke**

Run: `python manage.py test customers -v 2`

Expected: all tests still pass (the stub landing test asserts "Village Tech" — base.html still includes it via the navbar once landing extends base, which happens in the next task; but for now the stub landing.html doesn't yet extend base, so tests still pass via the stub. Confirm green.)

---

## Task 8: Landing page — hero, story, categories

**Files:**
- Modify: `templates/landing.html` (replace the stub)
- Modify: `static/css/styles.css` (append hero & category styles)

- [ ] **Step 1: Replace `templates/landing.html` with the first half of the real page**

(You'll add the remaining sections — how-it-works, why-us, form, contact — in Tasks 9–10. For now write a complete file with the first three sections plus placeholders for the rest, so the page still renders.)

Replace `templates/landing.html` with:
```html
{% extends "base.html" %}
{% load static %}

{% block content %}

<!-- ============ HERO ============ -->
<section class="vt-hero">
  <div class="container">
    <div class="row align-items-center g-4">
      <div class="col-lg-7 text-center text-lg-start">
        <span class="vt-eyebrow">Doorstep delivery · Chennai</span>
        <h1 class="vt-hero-title">
          Fresh <span class="vt-accent">groceries</span>,
          <span class="vt-accent">meat</span> &amp;
          <span class="vt-accent">veggies</span><br>
          right at your door.
        </h1>
        <p class="vt-hero-sub">
          Chicken, mutton, duck, fish, fresh vegetables and daily groceries —
          delivered the same day. Register once and we'll call you for every order.
        </p>
        <div class="d-flex gap-2 justify-content-center justify-content-lg-start flex-wrap">
          <a href="#register" class="btn vt-btn-primary btn-lg">Register Now</a>
          <a href="tel:{{ brand_phone }}" class="btn vt-btn-outline btn-lg">📞 Call {{ brand_phone }}</a>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="vt-hero-art" aria-hidden="true">
          <div class="vt-hero-emoji">🛒🥬🍗🐟</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ============ STORY ============ -->
<section class="vt-section vt-section-light">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8 text-center">
        <h2>Our story</h2>
        <p class="lead mb-3">
          {{ brand_name }} started from a simple wish — fresh meat and vegetables
          should be one phone call away, not a long auto ride to the market.
        </p>
        <p class="text-muted">
          We source from local farmers and butchers every morning, clean and pack
          everything carefully, and bring it to your door the same day. No middlemen,
          fair price, real freshness.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- ============ CATEGORIES ============ -->
<section class="vt-section">
  <div class="container">
    <h2 class="text-center mb-4">What we deliver</h2>
    <div class="row g-3 g-md-4">
      {% for item in categories %}
      <div class="col-6 col-md-4">
        <div class="vt-category-card text-center h-100">
          <div class="vt-category-emoji">{{ item.emoji }}</div>
          <div class="vt-category-label">{{ item.label }}</div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</section>

<!-- ============ PLACEHOLDERS for the remaining sections — filled in Task 9 ============ -->
<section id="how" class="vt-section vt-section-light">
  <div class="container text-center">
    <h2>How it works</h2>
    <p class="text-muted">(filled in next task)</p>
  </div>
</section>

<section id="register" class="vt-section">
  <div class="container text-center">
    <h2>Register</h2>
    <p class="text-muted">(form moves here in Task 10)</p>
    <!-- Temporary stub form so submit still works during the build -->
    <form method="post" action="{% url 'customers:register' %}" class="mx-auto" style="max-width:480px">
      {% csrf_token %}
      {{ form.as_p }}
      <button type="submit" class="btn vt-btn-primary btn-lg w-100">Register</button>
    </form>
  </div>
</section>

{% endblock %}
```

- [ ] **Step 2: Pass the `categories` context to the landing view**

In `customers/views.py`, replace the `landing` function with:
```python
CATEGORIES = [
    {"emoji": "🛒", "label": "Groceries"},
    {"emoji": "🍗", "label": "Chicken"},
    {"emoji": "🍖", "label": "Mutton"},
    {"emoji": "🦆", "label": "Duck"},
    {"emoji": "🐟", "label": "Fish"},
    {"emoji": "🥬", "label": "Vegetables"},
]


@require_http_methods(["GET", "POST"])
def landing(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # Submitting from the inline form posts to /register/, but accept POST
        # here too for resilience — delegate to the register view's logic.
        return register(request)
    form = CustomerForm()
    return render(
        request,
        "landing.html",
        {"form": form, "categories": CATEGORIES},
    )
```

Also update the `register` view so its "invalid → re-render landing" branch passes the categories too — replace the existing `register` function with:
```python
@require_http_methods(["GET", "POST"])
def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect(
                f"{reverse('customers:thank_you')}?phone={customer.phone}"
            )
        return render(
            request,
            "landing.html",
            {
                "form": form,
                "categories": CATEGORIES,
                "scroll_to_form": True,
            },
            status=200,
        )
    return redirect("customers:landing")
```

- [ ] **Step 3: Append hero and category styles to `static/css/styles.css`**

Append this block to the bottom of `static/css/styles.css`:
```css
/* ===== Hero ===== */
.vt-hero {
  background: linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%);
  padding: clamp(2rem, 6vw, 5rem) 0;
}
.vt-eyebrow {
  display: inline-block;
  background: var(--vt-green);
  color: #fff;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}
.vt-hero-title { color: var(--vt-green-dark); margin-bottom: 1rem; }
.vt-hero-title .vt-accent { color: var(--vt-orange); }
.vt-hero-sub { font-size: 1.05rem; color: #444; margin-bottom: 1.25rem; }
.vt-hero-art {
  background: #fff;
  border-radius: 24px;
  padding: 1.5rem;
  box-shadow: 0 20px 40px -20px rgba(46, 125, 50, 0.35);
  text-align: center;
}
.vt-hero-emoji { font-size: clamp(3rem, 14vw, 6rem); line-height: 1.2; letter-spacing: 0.25rem; }

/* ===== Sections ===== */
.vt-section { padding: clamp(2rem, 5vw, 4rem) 0; }
.vt-section-light { background: #fff; }
.vt-section h2 { color: var(--vt-green-dark); }

/* ===== Category cards ===== */
.vt-category-card {
  background: #fff;
  border: 2px solid transparent;
  border-radius: 18px;
  padding: 1.25rem 0.75rem;
  box-shadow: 0 6px 16px -10px rgba(0,0,0,0.2);
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.vt-category-card:hover {
  transform: translateY(-3px);
  border-color: var(--vt-orange);
}
.vt-category-emoji { font-size: 2.5rem; margin-bottom: 0.4rem; }
.vt-category-label { font-weight: 600; color: var(--vt-green-dark); }
```

- [ ] **Step 4: Smoke-test the page**

Run: `python manage.py runserver`
Open `http://127.0.0.1:8000/`. You should see:
- Sticky top nav with brand + Register button.
- Hero with eyebrow chip, big title, sub-text, two buttons.
- "Our story" section.
- Six category cards in a 2-column (mobile) / 3-column (md+) grid.
- Placeholder "How it works" and "Register" sections (filled next tasks).

Resize the browser to ~360px wide and confirm it looks good on mobile width. Stop the server.

- [ ] **Step 5: Run tests**

Run: `python manage.py test customers -v 2`

Expected: all tests still pass.

---

## Task 9: Landing page — how-it-works and why-choose-us

**Files:**
- Modify: `templates/landing.html` (replace the "How it works" placeholder section and add "Why choose us")
- Modify: `static/css/styles.css` (append step + why styles)

- [ ] **Step 1: Replace the "How it works" placeholder section in `templates/landing.html`**

Find this block in `templates/landing.html`:
```html
<section id="how" class="vt-section vt-section-light">
  <div class="container text-center">
    <h2>How it works</h2>
    <p class="text-muted">(filled in next task)</p>
  </div>
</section>
```

Replace it with:
```html
<!-- ============ HOW IT WORKS ============ -->
<section id="how" class="vt-section vt-section-light">
  <div class="container">
    <h2 class="text-center mb-4">How it works</h2>
    <div class="row g-3 g-md-4">
      <div class="col-12 col-md-4">
        <div class="vt-step">
          <div class="vt-step-num">1</div>
          <h3 class="vt-step-title">Register</h3>
          <p class="vt-step-text">Fill the short form with your name, phone, and area.</p>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="vt-step">
          <div class="vt-step-num">2</div>
          <h3 class="vt-step-title">We call you</h3>
          <p class="vt-step-text">Our team rings you on the number you provided to confirm your order.</p>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="vt-step">
          <div class="vt-step-num">3</div>
          <h3 class="vt-step-title">We deliver</h3>
          <p class="vt-step-text">Fresh goods reach your door the same day, no fuss.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ============ WHY CHOOSE US ============ -->
<section class="vt-section">
  <div class="container">
    <h2 class="text-center mb-4">Why choose us</h2>
    <div class="row g-3 g-md-4">
      <div class="col-6 col-md-3">
        <div class="vt-why text-center">
          <div class="vt-why-icon">🌿</div>
          <div class="vt-why-label">Fresh</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="vt-why text-center">
          <div class="vt-why-icon">🏡</div>
          <div class="vt-why-label">Local</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="vt-why text-center">
          <div class="vt-why-icon">⚡</div>
          <div class="vt-why-label">Fast</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="vt-why text-center">
          <div class="vt-why-icon">💰</div>
          <div class="vt-why-label">Fair price</div>
        </div>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append step and why-card styles to `static/css/styles.css`**

Append this block to the bottom of `static/css/styles.css`:
```css
/* ===== Steps ===== */
.vt-step {
  background: var(--vt-cream);
  border-radius: 18px;
  padding: 1.5rem 1.25rem;
  height: 100%;
  border-left: 6px solid var(--vt-orange);
}
.vt-step-num {
  display: inline-block;
  width: 2.25rem;
  height: 2.25rem;
  line-height: 2.25rem;
  text-align: center;
  background: var(--vt-orange);
  color: #fff;
  border-radius: 50%;
  font-weight: 700;
  margin-bottom: 0.75rem;
}
.vt-step-title { color: var(--vt-green-dark); font-size: 1.15rem; margin-bottom: 0.4rem; }
.vt-step-text { color: #444; margin: 0; }

/* ===== Why cards ===== */
.vt-why {
  background: #fff;
  border-radius: 18px;
  padding: 1.25rem 0.75rem;
  box-shadow: 0 6px 16px -10px rgba(0,0,0,0.15);
  height: 100%;
}
.vt-why-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.vt-why-label { font-weight: 600; color: var(--vt-green-dark); }
```

- [ ] **Step 3: Smoke-test the page**

Run: `python manage.py runserver`
Open `/`. Confirm:
- "How it works" shows 3 cards with orange numbered circles.
- "Why choose us" shows 4 cards in a 2x2 grid on mobile, 1x4 on desktop.
Stop the server.

- [ ] **Step 4: Run tests**

Run: `python manage.py test customers -v 2`

Expected: all tests pass.

---

## Task 10: Landing page — final inline register form

**Files:**
- Modify: `templates/landing.html` (replace the temporary stub register section)
- Modify: `static/css/styles.css` (append form styles)

- [ ] **Step 1: Replace the stub `#register` section in `templates/landing.html`**

Find this block:
```html
<section id="register" class="vt-section">
  <div class="container text-center">
    <h2>Register</h2>
    <p class="text-muted">(form moves here in Task 10)</p>
    <!-- Temporary stub form so submit still works during the build -->
    <form method="post" action="{% url 'customers:register' %}" class="mx-auto" style="max-width:480px">
      {% csrf_token %}
      {{ form.as_p }}
      <button type="submit" class="btn vt-btn-primary btn-lg w-100">Register</button>
    </form>
  </div>
</section>
```

Replace it with:
```html
<!-- ============ REGISTER FORM ============ -->
<section id="register" class="vt-section vt-section-light">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6">
        <div class="vt-form-card">
          <h2 class="text-center mb-1">Register for delivery</h2>
          <p class="text-center text-muted mb-4">
            Takes 20 seconds. We'll call you on the number you give us.
          </p>

          <form method="post" action="{% url 'customers:register' %}" novalidate id="vt-register-form">
            {% csrf_token %}

            {% if form.non_field_errors %}
              <div class="alert alert-danger">{{ form.non_field_errors }}</div>
            {% endif %}

            <div class="mb-3">
              <label for="{{ form.name.id_for_label }}" class="form-label fw-semibold">Name</label>
              {{ form.name }}
              {% if form.name.errors %}<div class="text-danger small mt-1">{{ form.name.errors|join:", " }}</div>{% endif %}
            </div>

            <div class="mb-3">
              <label for="{{ form.phone.id_for_label }}" class="form-label fw-semibold">Phone (10 digits)</label>
              {{ form.phone }}
              {% if form.phone.errors %}<div class="text-danger small mt-1">{{ form.phone.errors|join:", " }}</div>{% endif %}
            </div>

            <div class="mb-3">
              <label for="{{ form.place.id_for_label }}" class="form-label fw-semibold">Place / Area</label>
              {{ form.place }}
              {% if form.place.errors %}<div class="text-danger small mt-1">{{ form.place.errors|join:", " }}</div>{% endif %}
            </div>

            <div class="mb-4">
              <label for="{{ form.notes.id_for_label }}" class="form-label fw-semibold">
                What you usually buy <span class="text-muted small">(optional)</span>
              </label>
              {{ form.notes }}
            </div>

            <button type="submit" class="btn vt-btn-primary btn-lg w-100" id="vt-submit-btn">
              Register Now
            </button>
            <p class="text-muted text-center small mt-3 mb-0">
              We never share your number. Just to call you back about orders.
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append form-card styles to `static/css/styles.css`**

Append this block to the bottom of `static/css/styles.css`:
```css
/* ===== Register form ===== */
.vt-form-card {
  background: #fff;
  border-radius: 24px;
  padding: clamp(1.5rem, 4vw, 2.5rem);
  box-shadow: 0 20px 40px -20px rgba(46, 125, 50, 0.3);
  border-top: 6px solid var(--vt-green);
}
.vt-form-card .form-control:focus {
  border-color: var(--vt-green);
  box-shadow: 0 0 0 0.2rem rgba(46, 125, 50, 0.18);
}
```

- [ ] **Step 3: Add a small inline script for smooth scroll + disable-on-submit**

In `templates/landing.html`, just before the closing `{% endblock %}`, add:
```html
<script>
  // Smooth-scroll to the form when the navbar/CTA "Register" is tapped.
  document.querySelectorAll('a[href="#register"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var el = document.getElementById('register');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // If we re-rendered with errors, scroll to the form on load.
  {% if scroll_to_form %}
  window.addEventListener('load', function () {
    var el = document.getElementById('register');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  {% endif %}

  // Prevent double submit.
  var form = document.getElementById('vt-register-form');
  var btn = document.getElementById('vt-submit-btn');
  if (form && btn) {
    form.addEventListener('submit', function () {
      btn.disabled = true;
      btn.textContent = 'Sending…';
      setTimeout(function () { btn.disabled = false; btn.textContent = 'Register Now'; }, 5000);
    });
  }
</script>
```

- [ ] **Step 4: Smoke-test the full landing page**

Run: `python manage.py runserver`

On `http://127.0.0.1:8000/`:
- Tap the navbar **Register** link — page smooth-scrolls to the form.
- Fill: Name=`Anbu`, Phone=`+91 96000 12345`, Place=`T. Nagar`, Notes=`rice & chicken`.
- Submit → redirected to `/thank-you/?phone=9600012345` (but you're using the stub thank-you template still — that's fine, it's polished in Task 11).
- Open admin → confirm the new row is there.

Try an invalid submit:
- Go back to `/`, empty the Name field, type `123` for phone, submit.
- Page should re-render with red error text under Name and Phone, and the form should be in view at the top.

Stop the server.

- [ ] **Step 5: Run tests**

Run: `python manage.py test customers -v 2`

Expected: all tests pass.

---

## Task 11: Polished thank-you page

**Files:**
- Modify: `templates/thank_you.html` (replace stub)

- [ ] **Step 1: Replace `templates/thank_you.html`**

Replace the contents of `templates/thank_you.html` with:
```html
{% extends "base.html" %}

{% block title %}Thank you — {{ brand_name }}{% endblock %}

{% block content %}
<section class="vt-section">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8 col-lg-6 text-center">
        <div class="vt-thanks-card">
          <div class="vt-thanks-emoji">🎉</div>
          <h1 class="mb-2">Thank you!</h1>
          <p class="lead mb-1">You're on the list.</p>
          <p class="mb-4">
            We'll call you soon at
            <strong class="vt-accent">{{ masked_phone }}</strong>.
          </p>

          <a href="{% url 'customers:landing' %}" class="btn vt-btn-outline">Back to home</a>
          <a href="https://wa.me/91{{ brand_phone }}?text=Hi%2C%20I%20just%20registered%20on%20{{ brand_name|urlencode }}%2C%20can%20you%20call%20me%3F"
             target="_blank" rel="noopener"
             class="btn vt-btn-primary ms-2">
            Chat on WhatsApp
          </a>
        </div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

- [ ] **Step 2: Append thank-you styles to `static/css/styles.css`**

Append this block to the bottom of `static/css/styles.css`:
```css
/* ===== Thank you ===== */
.vt-thanks-card {
  background: #fff;
  border-radius: 24px;
  padding: clamp(2rem, 5vw, 3rem) clamp(1.25rem, 4vw, 2.5rem);
  box-shadow: 0 20px 40px -20px rgba(46, 125, 50, 0.3);
  border-top: 8px solid var(--vt-yellow);
}
.vt-thanks-emoji { font-size: 4rem; line-height: 1; margin-bottom: 0.5rem; }
.vt-thanks-card .vt-accent { color: var(--vt-orange); }
```

- [ ] **Step 3: Smoke-test the thank-you page**

Run: `python manage.py runserver`
- Register a new customer with a valid phone.
- On the thank-you page confirm:
  - Big 🎉 emoji visible.
  - "We'll call you soon at **96000-XXXXX**" (masked).
  - "Back to home" and "Chat on WhatsApp" buttons work.
- Refresh the thank-you page — no duplicate row in admin (it's a GET, not a re-POST).
Stop the server.

- [ ] **Step 4: Run tests**

Run: `python manage.py test customers -v 2`

Expected: all tests pass.

---

## Task 12: Mobile responsiveness check + README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Open the site in a real mobile browser (or Chrome DevTools mobile mode)**

Run: `python manage.py runserver 0.0.0.0:8000`

From your phone on the same Wi-Fi, open `http://<your-laptop-ip>:8000/`. Confirm on a real device:
- Hero text is readable, buttons full-width-ish and tappable.
- Category grid is 2 columns; each card big enough to tap.
- Form inputs are large (`form-control-lg`) and easy to tap.
- Tapping the phone number in the footer opens the dialer.
- Tapping the WhatsApp link opens WhatsApp.

If anything looks cramped, tweak `clamp()` values in `styles.css` and re-test.

Stop the server.

- [ ] **Step 2: Create `README.md`**

Create `README.md` with this exact content:
```markdown
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
```

- [ ] **Step 3: Final full test run**

Run: `python manage.py test -v 2`

Expected: all tests pass (23 total — 4 model + 4 admin + 9 form + 6 view).

- [ ] **Step 4: Final manual smoke test**

Run: `python manage.py runserver` and walk through the full happy path one more time:
1. Open `/`.
2. Scroll through every section.
3. Submit the form with a fresh phone number.
4. Confirm thank-you page shows masked phone.
5. Open `/admin/` and confirm the new row appears with `contacted = False`.
6. Toggle `contacted` in the admin list view, confirm it sticks after refresh.

Stop the server. Project is done.

---

## Self-Review — done

Spec coverage check (each spec section → which task):
- §2 Goals → all (Tasks 1-12)
- §3 Non-goals → respected (no cart/login/payment built)
- §4 User flows → Tasks 6, 8-11 (visitor) and Task 4 (owner)
- §5 Site map → Task 6 (URLs)
- §6 Landing page sections → Tasks 7-10
- §7 Registration form → Task 5 (form) and Task 10 (template)
- §8 Data model → Task 3
- §9 Admin → Task 4
- §10 Tech stack → Tasks 1-2
- §11 Project structure → Tasks 1-2 (verified at end of Task 12)
- §12 Visual design → Tasks 7-11 (CSS)
- §13 Security/privacy → Task 1 (env-based SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- §14 Testing → all TDD tasks (3, 4, 5, 6); manual smoke in Task 12
- §15 Deployment → out of scope (informational only in spec)

No placeholders. No `TBD`/`TODO`. All steps include the exact code or exact command. URL names, model fields, and view function names are consistent across tasks.
