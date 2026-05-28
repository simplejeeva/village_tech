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
