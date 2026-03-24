"""
Module: Audit Log
Table: AuditLog — records all important system actions
"""
from django.db import models
from apps.authentication.models import User


class AuditLog(models.Model):
    ACTION_INSERT = "INSERT"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_APPROVE = "APPROVE"
    ACTION_REJECT = "REJECT"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100, null=True, blank=True)
    record_id = models.IntegerField(null=True, blank=True)
    old_data = models.TextField(null=True, blank=True)
    new_data = models.TextField(null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    action_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "AuditLog"
        ordering = ["-action_at"]

    def __str__(self):
        return f"[{self.action}] {self.table_name} #{self.record_id} by {self.user}"
