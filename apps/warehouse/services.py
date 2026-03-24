from django.db import transaction
from .models import GoodsReceipt, DepartmentConfirmation
from apps.requisition.models import PurchaseRequisition
from apps.cart.models import PurchaseOrder


class WarehouseService:
    @staticmethod
    @transaction.atomic
    def create_goods_receipt(data, received_by):
        lines_data = data.pop("lines", [])
        receipt = GoodsReceipt.objects.create(received_by=received_by, **data)
        all_complete = True
        from .models import GoodsReceiptLine
        for ld in lines_data:
            line = GoodsReceiptLine.objects.create(receipt=receipt, **ld)
            if line.quantity_received < line.quantity_ordered:
                all_complete = False
        receipt.status = (
            GoodsReceipt.STATUS_COMPLETE if all_complete else GoodsReceipt.STATUS_PARTIAL
        )
        receipt.save(update_fields=["status"])
        # Notify dept heads
        from apps.notifications.services import NotificationService
        NotificationService.notify_goods_received(receipt)
        return receipt

    @staticmethod
    @transaction.atomic
    def confirm_receipt(receipt_line, confirmed_by, quality_note=""):
        DepartmentConfirmation.objects.create(
            receipt_line=receipt_line,
            pr=receipt_line.pr,
            confirmed_by=confirmed_by,
            quality_note=quality_note,
        )
        if receipt_line.pr:
            receipt_line.pr.status = PurchaseRequisition.STATUS_RECEIVED
            receipt_line.pr.save(update_fields=["status"])
        # Check if all lines confirmed → close order
        order = receipt_line.receipt.order
        all_prs_done = not order.lines.filter(
            pr_links__pr__status__in=[
                PurchaseRequisition.STATUS_PROCESSING,
                PurchaseRequisition.STATUS_IN_CART,
            ]
        ).exists()
        if all_prs_done:
            order.status = PurchaseOrder.STATUS_DELIVERED
            order.save(update_fields=["status", "updated_at"])
