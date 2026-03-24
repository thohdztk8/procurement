"""Celery tasks for async notifications."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task(bind=True, queue="notifications")
def send_notification_email(self, notification_id):
    from .models import Notification
    try:
        n = Notification.objects.select_related("recipient").get(pk=notification_id)
        if n.is_email_sent:
            return
        send_mail(
            subject=n.title,
            message=n.message or n.title,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[n.recipient.email],
            fail_silently=True,
        )
        n.is_email_sent = True
        n.email_sent_at = timezone.now()
        n.save(update_fields=["is_email_sent", "email_sent_at"])
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(queue="notifications")
def send_quotation_email(session_id):
    from apps.quotation.models import QuotationSession
    try:
        session = QuotationSession.objects.select_related(
            "order_supplier__supplier", "order"
        ).get(pk=session_id)
        contact = (
            session.order_supplier.supplier.contacts.filter(is_primary=True, is_active=True).first()
            or session.order_supplier.supplier.contacts.filter(is_active=True).first()
        )
        if not contact:
            return
        portal_url = session.get_portal_url()
        send_mail(
            subject=f"Yêu cầu báo giá — Order {session.order.order_number}",
            message=(
                f"Kính gửi {contact.contact_name},\n\n"
                f"Chúng tôi gửi yêu cầu báo giá cho đơn hàng {session.order.order_number}.\n"
                f"Vui lòng truy cập link dưới để nhập báo giá "
                f"(hạn: {session.token_expiry.strftime('%d/%m/%Y %H:%M')}):\n\n"
                f"{portal_url}\n\n"
                f"Trân trọng,\nPhòng Mua hàng"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            fail_silently=True,
        )
    except Exception:
        pass
