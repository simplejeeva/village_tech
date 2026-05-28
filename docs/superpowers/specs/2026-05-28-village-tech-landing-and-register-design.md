# Village Tech — Landing Page & Customer Registration

**Date:** 2026-05-28
**Status:** Approved design, ready for implementation plan
**Owner:** Jeevananthan (jeevananthan.p@techjays.com)

---

## 1. Background

Jeevananthan is launching **Village Tech**, a doorstep delivery business for groceries, meat (chicken, mutton, duck, fish), and vegetables. Most prospective customers will visit from a mobile phone. The first version of the website does **not** need product browsing, cart, online payment, or customer accounts — it needs to:

1. Tell the brand story in a warm, colorful way.
2. Collect customer interest via a simple registration form (name, phone, place).
3. Let the owner see all registrations in a private admin panel and call them back.

This is a marketing + lead-capture site, not an e-commerce site.

---

## 2. Goals

- Single colorful landing page that explains who Village Tech is and what it delivers.
- One simple registration form (no login, no signup, no password).
- Mobile-first responsive design — must look great on a phone first, desktop second.
- Owner sees every registration in Django admin and can mark them as contacted.
- Fast to ship: standard Django, default SQLite, no build pipeline.

## 3. Non-goals (out of scope for v1)

- Online ordering, cart, payments.
- Product catalogue with prices.
- Customer accounts / login / password reset.
- Email or SMS notifications to the customer.
- Multi-language support (English only for v1; can add Tamil later).
- Production deployment automation (hosting decision is deferred).

---

## 4. User flows

### 4.1 Visitor flow (mobile)
1. Visitor opens the site URL on their phone.
2. Sees a colorful hero with business name and "Register Now" button.
3. Scrolls through: story → categories → how-it-works → why-choose-us → contact.
4. Taps "Register Now" — page scrolls to inline form (no navigation away).
5. Fills name, phone, place, optional notes → taps Submit.
6. Sees a thank-you screen confirming the phone number we will call.

### 4.2 Owner flow (admin)
1. Owner opens `/admin/` and logs in with the Django superuser account.
2. Sees the **Customers** table with newest registrations first.
3. Clicks a row to see full details.
4. Toggles a **Contacted** checkbox once they have called the customer.
5. Can filter by Contacted state and search by phone or place.
6. Can export selected rows to CSV (built-in Django admin action).

---

## 5. Site map

| Path | Purpose |
|------|---------|
| `/` | Landing page with inline registration form |
| `/register/` | POST endpoint for form submission (also accepts GET as a fallback that renders the same form on its own page) |
| `/thank-you/` | Post-submit confirmation page |
| `/admin/` | Django admin — owner only |

---

## 6. Landing page sections

Top to bottom on a mobile screen:

1. **Hero** — Brand name "Village Tech", tagline "Fresh groceries & meat at your doorstep", a vibrant photo or illustration, prominent "Register Now" button that scrolls to the form.
2. **Our story** — Two short paragraphs about the founder's motivation and the freshness/local-sourcing angle.
3. **What we deliver** — 6 cards with emoji + label: Groceries, Chicken, Mutton, Duck, Fish, Vegetables. Two columns on mobile, three on desktop.
4. **How it works** — 3 numbered steps with icons: Register → We call you → We deliver.
5. **Why choose us** — 4 small cards: Fresh, Local, Fast, Fair price.
6. **Register form** — Inline form on the same page (anchor `#register`).
7. **Contact footer** — Phone number `9600877537` as a `tel:` link, WhatsApp link (`https://wa.me/919600877537`), and the business name.

---

## 7. Registration form

### 7.1 Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | CharField(max_length=80) | Yes | Stripped, non-empty after strip |
| `phone` | CharField(max_length=15) | Yes | Must contain exactly 10 digits after stripping non-digits; stored in normalized 10-digit form |
| `place` | CharField(max_length=120) | Yes | Stripped, non-empty after strip |
| `notes` | TextField(blank=True) | No | Max 500 chars |

### 7.2 Submission behaviour

- On valid POST: save a `Customer` row, redirect (HTTP 302) to `/thank-you/?phone=<masked>` so a browser refresh on the thank-you page does not resubmit.
- On invalid POST: re-render the landing page with the form scrolled into view, errors shown beside the offending field, previously entered values preserved.
- Submit button is disabled (client-side) for ~3 seconds after click to prevent double-submits; the server is also idempotent via a soft-dedupe check (same phone + same place submitted within the last 60 seconds is treated as the existing entry).

### 7.3 Thank-you page

- Heading: "Thank you! 🎉"
- Body: "We will call you soon at 96008-XXXXX" (last 5 digits masked using the value carried in the query string).
- A small button to return to the landing page.

---

## 8. Data model

Single model in the `customers` app:

```
Customer
  - name           CharField(80)
  - phone          CharField(15, db_index=True)
  - place          CharField(120)
  - notes          TextField(blank=True)
  - contacted      BooleanField(default=False)
  - created_at     DateTimeField(auto_now_add=True, db_index=True)

  Meta:
    ordering = ["-created_at"]

  __str__:
    f"{name} ({phone}) — {place}"
```

No foreign keys, no related tables. SQLite is sufficient.

---

## 9. Django admin configuration

- `list_display`: `name`, `phone`, `place`, `contacted`, `created_at`
- `list_filter`: `contacted`, `created_at`
- `search_fields`: `name`, `phone`, `place`
- `list_editable`: `contacted` (toggle directly from the list view)
- `date_hierarchy`: `created_at`
- `actions`: a custom "Mark selected as contacted" action in addition to the built-in CSV export pattern (use Django's `admin.action` decorator).

---

## 10. Tech stack & dependencies

- **Python 3.11+**
- **Django 5.x**
- **SQLite** (Django default — no extra config)
- **Bootstrap 5** via CDN (no Node, no build step)
- **Whitenoise** for serving static files in a single-process deployment
- `python-dotenv` for reading `SECRET_KEY` from a `.env` file

No frontend framework, no REST API, no JavaScript build pipeline. A small amount of vanilla JS for: smooth-scroll to the form anchor, disable-on-submit, and a simple client-side phone-format hint.

---

## 11. Project structure

```
delivery/
├── manage.py
├── db.sqlite3                    (created on first migrate)
├── .env.example                  (template — real .env is git-ignored)
├── requirements.txt
├── README.md
├── village_tech/                 (project package)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── customers/                    (the app)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── tests.py
├── templates/
│   ├── base.html                 (Bootstrap + brand colors + header/footer)
│   ├── landing.html              (extends base; all sections)
│   └── thank_you.html
└── static/
    ├── css/
    │   └── styles.css            (brand colors, hero, cards)
    └── images/
        └── (hero & category images, sourced or placeholder)
```

---

## 12. Visual design

### 12.1 Palette
- Primary green `#2E7D32` (buttons, accents, headings)
- Warm orange `#FB8C00` (CTA highlights, hover states)
- Sunny yellow `#FFC107` (small badges, stars)
- Cream background `#FFF8E1` (page background)
- Text dark `#212121`

### 12.2 Typography
- Headings: a friendly bold font via Google Fonts (e.g. **Poppins** 600/700).
- Body: **Poppins** 400 / system fallback.
- Mobile base size: 16px; headings scale via `clamp()` for fluid sizing.

### 12.3 Imagery
- One hero image (vegetables + meat platter or a friendly delivery scene).
- Six category icons or photos (emoji as fallback if no photo).
- All images served from `static/images/`, lazy-loaded with `loading="lazy"`.

### 12.4 Responsive breakpoints
- Mobile-first base styles.
- Tablet: `min-width: 768px` — categories grid becomes 3 columns.
- Desktop: `min-width: 1024px` — hero becomes a 2-column layout with form on the right.

---

## 13. Security & privacy

- CSRF protection enabled on the form (Django default).
- `DEBUG=False` in production; `SECRET_KEY` read from `.env`.
- `ALLOWED_HOSTS` configured per environment.
- The admin URL stays at the default `/admin/` for v1; can be moved to an obscure path later if needed.
- Phone numbers are personal data — admin access is restricted to the superuser; no public endpoint exposes the customer list.
- No third-party analytics or trackers in v1.

---

## 14. Testing

Pragmatic, not exhaustive — this is a small site.

- `customers/tests.py` covers:
  - Form accepts a valid submission and creates a `Customer`.
  - Form rejects missing required fields.
  - Form rejects a phone with fewer or more than 10 digits.
  - Duplicate (same phone + same place) within 60 seconds is treated as the existing row (no duplicate created).
  - Landing page returns 200 and contains the brand name.
  - Thank-you page returns 200 and masks the phone.
- Manual smoke test on a real phone (Chrome on Android) before declaring done — landing renders, form submits, thank-you appears, admin shows the row.

---

## 15. Deployment (deferred — informational only)

- Local dev: `python manage.py runserver`.
- Future hosting decision (PythonAnywhere, Railway, Render, or a VPS) is deferred to after the implementation plan is approved and the code is working locally.
- A `Procfile`-style entry point and a production checklist will be added when hosting is chosen, not now.

---

## 16. Open questions

None blocking. Items below can be decided during or after implementation:

- Exact hero image (placeholder for now, real photo later).
- Whether to add Tamil-language text alongside English in a future iteration.
- Whether to wire up a WhatsApp click-to-chat pre-filled message after registration.
