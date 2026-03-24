"""Business logic for Cart and Order operations."""
from django.db import transaction
from django.utils import timezone
from .models import Cart, CartItem, CartHistory, PurchaseOrder, OrderLine, OrderLinePR, OrderSupplier
from apps.requisition.models import PurchaseRequisition
from apps.master_data.models import Supplier


class CartService:
    @staticmethod
    @transaction.atomic
    def add_pr_to_cart(cart, pr, user, quantity_override=None, item_name_override=None):
        if CartItem.objects.filter(cart=cart, pr=pr, removed_at__isnull=True).exists():
            raise ValueError(f"PR {pr.pr_number} đã có trong cart này.")
        if pr.status != PurchaseRequisition.STATUS_PENDING:
            raise ValueError(f"PR {pr.pr_number} không ở trạng thái Chờ xử lý.")
        item = CartItem.objects.create(
            cart=cart, pr=pr, added_by=user,
            quantity_override=quantity_override,
            item_name_override=item_name_override,
        )
        pr.status = PurchaseRequisition.STATUS_IN_CART
        pr.save(update_fields=["status"])
        CartHistory.objects.create(cart=cart, changed_by=user, change_type="item_added", pr=pr)
        return item

    @staticmethod
    @transaction.atomic
    def remove_pr_from_cart(cart, pr, user):
        item = CartItem.objects.filter(cart=cart, pr=pr, removed_at__isnull=True).first()
        if not item:
            raise ValueError("PR không có trong cart.")
        item.removed_at = timezone.now()
        item.removed_by = user
        item.save()
        pr.status = PurchaseRequisition.STATUS_PENDING
        pr.save(update_fields=["status"])
        CartHistory.objects.create(cart=cart, changed_by=user, change_type="item_removed", pr=pr)


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart, supplier_ids, user, notes=""):
        if cart.status != Cart.STATUS_OPEN:
            raise ValueError("Cart không còn ở trạng thái mở.")
        active_items = CartItem.objects.filter(cart=cart, removed_at__isnull=True).select_related("pr__item")
        if not active_items.exists():
            raise ValueError("Cart không có vật tư nào.")
        order = PurchaseOrder.objects.create(cart=cart, created_by=user, notes=notes)
        # Group items by item (for same items from different PRs)
        item_map = {}
        for ci in active_items:
            key = (ci.pr.item_id, ci.effective_item_name())
            if key not in item_map:
                item_map[key] = {
                    "item": ci.pr.item,
                    "name": ci.effective_item_name(),
                    "uom": ci.pr.unit_of_measure,
                    "qty": 0,
                    "prs": [],
                }
            item_map[key]["qty"] += float(ci.effective_quantity())
            item_map[key]["prs"].append((ci.pr, float(ci.effective_quantity())))
        for key, data in item_map.items():
            line = OrderLine.objects.create(
                order=order,
                item=data["item"],
                item_name_display=data["name"],
                unit_of_measure=data["uom"],
                total_quantity=data["qty"],
            )
            for pr, qty in data["prs"]:
                OrderLinePR.objects.create(order_line=line, pr=pr, quantity=qty)
                pr.status = PurchaseRequisition.STATUS_PROCESSING
                pr.save(update_fields=["status"])
        for sid in supplier_ids:
            supplier = Supplier.objects.get(pk=sid)
            OrderSupplier.objects.create(order=order, supplier=supplier, added_by=user)
        cart.status = Cart.STATUS_CONVERTED
        cart.save(update_fields=["status"])
        return order
