from django.urls import path

from customers import views

app_name = "customers"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register, name="register"),
    path("thank-you/", views.thank_you, name="thank_you"),
    path("customer/", views.customer_list, name="customer_list"),
    path("customer/login/", views.customer_login, name="customer_login"),
    path("customer/logout/", views.customer_logout, name="customer_logout"),
]
