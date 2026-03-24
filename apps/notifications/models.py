"""
Module: Notifications
Table: Notification
"""
from django.db import models
from apps.authentication.models import User


class Notification(models.Model):
    EVENT_PR_CREATED = "pr_created"
    EVENT_PR_CANCELLED = "pr_cancelled"
    EVENT_QUOTATION_SENT = "quotation_sent"
    EVENT_QUOTATION_SUBMITTED = "quotation_submitted"
    EVENT_IPO_PENDING = "ipo_pending_approval"
    EVENT_IPO_APPROVED = "ipo_approved"
    EVENT_IPO_REJECTED = "ipo_rejected"
    EVENT_GOODS_RECEIVED = "goods_received"
    EVENT_PAYMENT_REQUEST = "payment_request_created"

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=2000, null=True, blank=True)
    entity_type = models.CharField(max_length=50, null=True, blank=True)
    entity_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Notification"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.event_type}] → {self.recipient.full_name}"
