from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import QuotationSession, QuotationLine, QuotationSubmitHistory
from apps.cart.models import PurchaseOrder, OrderSupplier


class QuotationService:
    @staticmethod
    @transaction.atomic
    def send_quotation_requests(order, supplier_ids, sent_by, expiry_hours=72):
        sessions = []
        expiry = timezone.now() + timedelta(hours=expiry_hours)
        for sid in supplier_ids:
            order_supplier = OrderSupplier.objects.get(order=order, supplier_id=sid)
            session, created = QuotationSession.objects.get_or_create(
                order=order,
                order_supplier=order_supplier,
                defaults={"token_expiry": expiry},
            )
            if not created:
                session.token_expiry = expiry
                session.status = QuotationSession.STATUS_PENDING
                session.save()
            # Create quotation lines for each order line
            for order_line in order.lines.all():
                QuotationLine.objects.get_or_create(
                    session=session, order_line=order_line
                )
            # Send email async
            from apps.notifications.tasks import send_quotation_email
            send_quotation_email.delay(session.pk)
            session.email_sent_at = timezone.now()
            session.email_sent_by = sent_by
            session.save(update_fields=["email_sent_at", "email_sent_by"])
            sessions.append(session)
        order.status = PurchaseOrder.STATUS_QUOTATION_SENT
        order.save(update_fields=["status", "updated_at"])
        return sessions

    @staticmethod
    @transaction.atomic
    def submit_quotation(session, lines_data, ip_address=""):
        if session.status == QuotationSession.STATUS_EXPIRED:
            raise ValueError("Phiên báo giá đã hết hạn.")
        if timezone.now() > session.token_expiry:
            session.status = QuotationSession.STATUS_EXPIRED
            session.save(update_fields=["status"])
            raise ValueError("Phiên báo giá đã hết hạn.")
        now = timezone.now()
        for line_data in lines_data:
            ql = QuotationLine.objects.get(pk=line_data["quotation_line_id"], session=session)
            unit_price = line_data.get("unit_price")
            qty = float(ql.order_line.total_quantity)
            ql.unit_price = unit_price
            ql.total_price = float(unit_price) * qty if unit_price else None
            ql.delivery_days = line_data.get("delivery_days")
            ql.notes = line_data.get("notes", "")
            ql.submitted_at = now
            ql.save()
        session.status = QuotationSession.STATUS_SUBMITTED
        session.save(update_fields=["status"])
        QuotationSubmitHistory.objects.create(
            session=session, ip_address=ip_address, submit_method="form"
        )
        # Update order status
        session.order.status = PurchaseOrder.STATUS_QUOTATION_RECEIVED
        session.order.save(update_fields=["status", "updated_at"])
