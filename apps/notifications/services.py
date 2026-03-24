"""Notification service — creates in-app notifications and queues emails."""
from .models import Notification
from apps.authentication.models import Role


class NotificationService:
    @staticmethod
    def _create(recipient, event_type, title, message="", entity_type=None, entity_id=None):
        from apps.notifications.tasks import send_notification_email
        n = Notification.objects.create(
            recipient=recipient,
            event_type=event_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        send_notification_email.delay(n.pk)
        return n

    @staticmethod
    def notify_pr_created(pr):
        from apps.authentication.models import User
        staff = User.objects.filter(
            role__role_code__in=[Role.PURCHASING_STAFF, Role.PURCHASING_MANAGER],
            is_active=True
        )
        for user in staff:
            NotificationService._create(
                user, Notification.EVENT_PR_CREATED,
                f"Yêu cầu mua hàng mới: {pr.pr_number}",
                f"Bộ phận {pr.department.department_name} đã tạo PR mới.",
                "PR", pr.pk
            )

    @staticmethod
    def notify_pr_cancelled(pr):
        NotificationService._create(
            pr.requested_by, Notification.EVENT_PR_CANCELLED,
            f"PR {pr.pr_number} đã bị hủy",
            f"Lý do: {pr.cancel_reason}", "PR", pr.pk
        )

    @staticmethod
    def notify_ipo_pending(ipo):
        from apps.authentication.models import User
        approvers = User.objects.filter(
            role__role_code__in=[Role.DIRECTOR, Role.VICE_DIRECTOR], is_active=True
        )
        for user in approvers:
            NotificationService._create(
                user, Notification.EVENT_IPO_PENDING,
                f"IPO chờ phê duyệt: {ipo.ipo_number}",
                f"Tổng giá trị: {ipo.total_amount:,.0f} {ipo.currency}",
                "IPO", ipo.pk
            )

    @staticmethod
    def notify_ipo_approved(ipo):
        NotificationService._create(
            ipo.created_by, Notification.EVENT_IPO_APPROVED,
            f"IPO {ipo.ipo_number} đã được phê duyệt",
            f"Phê duyệt bởi {ipo.approved_by.full_name}.", "IPO", ipo.pk
        )

    @staticmethod
    def notify_ipo_rejected(ipo):
        NotificationService._create(
            ipo.created_by, Notification.EVENT_IPO_REJECTED,
            f"IPO {ipo.ipo_number} bị từ chối",
            f"Lý do: {ipo.rejection_reason}", "IPO", ipo.pk
        )

    @staticmethod
    def notify_goods_received(receipt):
        from apps.authentication.models import User
        dept_heads = User.objects.filter(
            role__role_code=Role.DEPT_HEAD, is_active=True
        )
        for user in dept_heads:
            NotificationService._create(
                user, Notification.EVENT_GOODS_RECEIVED,
                f"Hàng đã nhập kho: {receipt.receipt_number}",
                f"Order {receipt.order.order_number} đã nhận hàng.",
                "GoodsReceipt", receipt.pk
            )

    @staticmethod
    def notify_payment_request(payment_request):
        from apps.authentication.models import User
        accountants = User.objects.filter(role__role_code=Role.ACCOUNTANT, is_active=True)
        for user in accountants:
            NotificationService._create(
                user, Notification.EVENT_PAYMENT_REQUEST,
                f"Yêu cầu thanh toán mới: {payment_request.request_number}",
                f"Số tiền: {payment_request.amount:,.0f} {payment_request.currency}. "
                f"Hạn: {payment_request.due_date}",
                "PaymentRequest", payment_request.pk
            )
