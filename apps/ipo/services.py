from django.db import transaction
from django.utils import timezone
from .models import IPO, IPOLine, IPOHistory
from apps.cart.models import PurchaseOrder


class IPOService:
    @staticmethod
    @transaction.atomic
    def create_ipo(order, lines_data, created_by, notes=""):
        ipo = IPO.objects.create(order=order, created_by=created_by, notes=notes)
        total = 0
        for ld in lines_data:
            line = IPOLine.objects.create(
                ipo=ipo,
                order_line_id=ld["order_line_id"],
                supplier_id=ld["supplier_id"],
                quotation_line_id=ld.get("quotation_line_id"),
                item_name_display=ld["item_name_display"],
                unit_of_measure=ld["unit_of_measure"],
                quantity=ld["quantity"],
                unit_price=ld["unit_price"],
                total_price=float(ld["quantity"]) * float(ld["unit_price"]),
                currency=ld.get("currency", "VND"),
                payment_term_days=ld.get("payment_term_days", 30),
                delivery_days=ld.get("delivery_days"),
                notes=ld.get("notes", ""),
            )
            total += float(line.total_price)
        ipo.total_amount = total
        ipo.save(update_fields=["total_amount"])
        IPOHistory.objects.create(
            ipo=ipo, changed_by=created_by, change_type="created",
            new_status=IPO.STATUS_DRAFT
        )
        return ipo

    @staticmethod
    @transaction.atomic
    def submit_for_approval(ipo, submitted_by):
        if ipo.status != IPO.STATUS_DRAFT:
            raise ValueError("Chỉ IPO ở trạng thái Nháp mới có thể submit duyệt.")
        old = ipo.status
        ipo.status = IPO.STATUS_PENDING
        ipo.submitted_at = timezone.now()
        ipo.save(update_fields=["status", "submitted_at", "updated_at"])
        IPOHistory.objects.create(
            ipo=ipo, changed_by=submitted_by, change_type="submitted",
            old_status=old, new_status=IPO.STATUS_PENDING
        )
        ipo.order.status = PurchaseOrder.STATUS_IPO_PENDING
        ipo.order.save(update_fields=["status", "updated_at"])
        from apps.notifications.services import NotificationService
        NotificationService.notify_ipo_pending(ipo)

    @staticmethod
    @transaction.atomic
    def approve(ipo, approved_by, notes=""):
        if ipo.status != IPO.STATUS_PENDING:
            raise ValueError("IPO không ở trạng thái Chờ duyệt.")
        old = ipo.status
        ipo.status = IPO.STATUS_APPROVED
        ipo.approved_at = timezone.now()
        ipo.approved_by = approved_by
        ipo.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])
        IPOHistory.objects.create(
            ipo=ipo, changed_by=approved_by, change_type="approved",
            old_status=old, new_status=IPO.STATUS_APPROVED, note=notes
        )
        ipo.order.status = PurchaseOrder.STATUS_IPO_APPROVED
        ipo.order.save(update_fields=["status", "updated_at"])
        from apps.notifications.services import NotificationService
        NotificationService.notify_ipo_approved(ipo)

    @staticmethod
    @transaction.atomic
    def reject(ipo, rejected_by, reason):
        if ipo.status != IPO.STATUS_PENDING:
            raise ValueError("IPO không ở trạng thái Chờ duyệt.")
        old = ipo.status
        ipo.status = IPO.STATUS_REJECTED
        ipo.rejected_at = timezone.now()
        ipo.rejected_by = rejected_by
        ipo.rejection_reason = reason
        ipo.save(update_fields=["status", "rejected_at", "rejected_by", "rejection_reason", "updated_at"])
        IPOHistory.objects.create(
            ipo=ipo, changed_by=rejected_by, change_type="rejected",
            old_status=old, new_status=IPO.STATUS_REJECTED, note=reason
        )
        ipo.order.status = PurchaseOrder.STATUS_IPO_REJECTED
        ipo.order.save(update_fields=["status", "updated_at"])
        from apps.notifications.services import NotificationService
        NotificationService.notify_ipo_rejected(ipo)
