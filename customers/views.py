import secrets
from functools import wraps

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from customers.forms import CustomerForm
from customers.models import Customer


DASHBOARD_SESSION_KEY = "vt_dashboard_ok"


def _require_dashboard_auth(view):
    """Gate a view behind the shared dashboard password session flag.

    When the flag is missing, send the visitor to /customer/login/ so they
    can enter the single shared password.
    """

    @wraps(view)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if not request.session.get(DASHBOARD_SESSION_KEY):
            return redirect("customers:customer_login")
        return view(request, *args, **kwargs)

    return wrapper


CATEGORIES = [
    {"emoji": "🛒", "label": "Groceries"},
    {"emoji": "🍗", "label": "Chicken"},
    {"emoji": "🍖", "label": "Mutton"},
    {"emoji": "🦆", "label": "Duck"},
    {"emoji": "🐟", "label": "Fish"},
    {"emoji": "🥬", "label": "Vegetables"},
]


def _mask_phone(raw: str | None) -> str:
    """Return the phone with its last 5 digits hidden, e.g. '96000-XXXXX'.

    Idempotent: a value that already looks masked is returned unchanged so
    a masked query string from /register/ does not get re-masked into the
    fallback. Falls back to 'your number' if input is missing or malformed.
    """
    if not raw:
        return "your number"
    if "X" in raw or "x" in raw:
        return raw
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) != 10:
        return "your number"
    return f"{digits[:5]}-XXXXX"


@require_http_methods(["GET", "POST"])
def landing(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # POSTing to / posts to the register flow.
        return register(request)
    form = CustomerForm()
    return render(
        request,
        "landing.html",
        {"form": form, "categories": CATEGORIES},
    )


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            # Carry only the masked phone in the URL so the raw number never
            # lands in browser history, server access logs, or the Referer
            # header sent to wa.me.
            masked = _mask_phone(customer.phone)
            return redirect(
                f"{reverse('customers:thank_you')}?phone={masked}"
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


@require_http_methods(["GET"])
def thank_you(request: HttpRequest) -> HttpResponse:
    masked = _mask_phone(request.GET.get("phone"))
    return render(request, "thank_you.html", {"masked_phone": masked})


@require_http_methods(["GET", "POST"])
def customer_login(request: HttpRequest) -> HttpResponse:
    """Single-password gate. No username — just the shared password."""
    error = None
    if request.method == "POST":
        password = request.POST.get("password", "")
        expected = getattr(settings, "DASHBOARD_PASSWORD", "") or ""
        if expected and secrets.compare_digest(password, expected):
            request.session[DASHBOARD_SESSION_KEY] = True
            return redirect("customers:customer_list")
        error = "Wrong password. Please try again."
    return render(request, "customer_login.html", {"error": error})


@require_http_methods(["GET", "POST"])
def customer_logout(request: HttpRequest) -> HttpResponse:
    request.session.pop(DASHBOARD_SESSION_KEY, None)
    return redirect("customers:customer_login")


@require_http_methods(["GET"])
@_require_dashboard_auth
def customer_list(request: HttpRequest) -> HttpResponse:
    """Private dashboard — reachable only after entering the shared password
    at /customer/login/. Not linked from the public site."""
    customers = Customer.objects.all()
    counts = {
        "total": customers.count(),
        "contacted": customers.filter(contacted=True).count(),
        "pending": customers.filter(contacted=False).count(),
    }
    return render(
        request,
        "customer_list.html",
        {"customers": customers, "counts": counts},
    )
