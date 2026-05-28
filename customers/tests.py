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

    def test_redirect_url_does_not_leak_raw_phone(self):
        """The redirect URL must carry only the masked phone, never the raw
        10-digit number — protects against PII leaking to server access logs
        and the outbound Referer header."""
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
        self.assertNotIn("9600012345", response.url)
        self.assertIn("96000-XXXXX", response.url)

    def test_thank_you_passes_already_masked_phone_through(self):
        """If thank_you is hit with an already-masked phone (the normal flow
        after our redirect), it must render the mask unchanged, not collapse
        to 'your number'."""
        response = self.client.get(
            reverse("customers:thank_you") + "?phone=96000-XXXXX"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "96000-XXXXX")

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


class CustomerDashboardTests(TestCase):
    """The /customer/ dashboard is gated by a single shared password
    stored in settings.DASHBOARD_PASSWORD. No Django user is involved."""

    def test_dashboard_redirects_to_password_page_when_unauthed(self):
        response = self.client.get(reverse("customers:customer_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("customers:customer_login"), response.url)

    def test_login_page_renders(self):
        response = self.client.get(reverse("customers:customer_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password")
        self.assertContains(response, 'name="password"')

    def test_correct_password_grants_access(self):
        response = self.client.post(
            reverse("customers:customer_login"),
            data={"password": "jeeva9600"},
            follow=True,
        )
        # Followed redirect should land us on the dashboard
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total registrations")

    def test_wrong_password_shows_error_and_blocks(self):
        response = self.client.post(
            reverse("customers:customer_login"),
            data={"password": "wrong-one"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wrong password")
        # Subsequent dashboard hit must still redirect to login
        check = self.client.get(reverse("customers:customer_list"))
        self.assertEqual(check.status_code, 302)
        self.assertIn(reverse("customers:customer_login"), check.url)

    def test_dashboard_lists_customers_after_login(self):
        self.client.post(
            reverse("customers:customer_login"),
            data={"password": "jeeva9600"},
        )
        Customer.objects.create(name="Anbu", phone="9600012345", place="T. Nagar")
        Customer.objects.create(
            name="Ravi", phone="9876543210", place="Velachery", contacted=True
        )
        response = self.client.get(reverse("customers:customer_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anbu")
        self.assertContains(response, "Ravi")
        self.assertContains(response, "9600012345")
        self.assertContains(response, "Already called")

    def test_logout_clears_session(self):
        self.client.post(
            reverse("customers:customer_login"),
            data={"password": "jeeva9600"},
        )
        # Logged in, dashboard accessible
        self.assertEqual(
            self.client.get(reverse("customers:customer_list")).status_code, 200
        )
        # Logout, then dashboard bounces back to login
        self.client.get(reverse("customers:customer_logout"))
        bounce = self.client.get(reverse("customers:customer_list"))
        self.assertEqual(bounce.status_code, 302)
        self.assertIn(reverse("customers:customer_login"), bounce.url)
