"""
Module: Reports & Statistics (UC-21)
Provides aggregated data endpoints for dashboards and exports.
"""
from datetime import date
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.authentication.permissions import IsApprover
from apps.authentication.models import Role
from apps.cart.models import PurchaseOrder
from apps.requisition.models import PurchaseRequisition
from apps.ipo.models import IPO
from apps.finance.models import Invoice, PaymentRequest
import io


def parse_date_range(request):
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    return date_from, date_to


class POStatusReportView(APIView):
    """Tình trạng PO — all purchasing roles."""

    def get(self, request):
        date_from, date_to = parse_date_range(request)
        qs = PurchaseOrder.objects.all()
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        by_status = qs.values("status").annotate(count=Count("id")).order_by("status")
        monthly = (
            qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        return Response({
            "total": qs.count(),
            "by_status": list(by_status),
            "monthly_trend": [
                {"month": r["month"].strftime("%Y-%m"), "count": r["count"]}
                for r in monthly if r["month"]
            ],
        })


class SupplierPerformanceReportView(APIView):
    def get(self, request):
        from apps.quotation.models import QuotationSession
        date_from, date_to = parse_date_range(request)
        qs = QuotationSession.objects.filter(status=QuotationSession.STATUS_SUBMITTED)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        by_supplier = (
            qs.values("order_supplier__supplier__company_name", "order_supplier__supplier__supplier_code")
            .annotate(
                total_quotations=Count("id"),
                selected=Count("lines", filter=Q(lines__is_selected=True)),
            )
            .order_by("-total_quotations")
        )
        return Response({"data": list(by_supplier)})


class SpendByCategoryReportView(APIView):
    def get(self, request):
        date_from, date_to = parse_date_range(request)
        dept = request.query_params.get("department")
        qs = Invoice.objects.filter(status=Invoice.STATUS_PAID)
        if date_from:
            qs = qs.filter(invoice_date__gte=date_from)
        if date_to:
            qs = qs.filter(invoice_date__lte=date_to)
        if dept:
            qs = qs.filter(order__cart__items__pr__department_id=dept)
        by_supplier = qs.values("supplier__company_name").annotate(
            total=Sum("total_amount")
        ).order_by("-total")
        return Response({"data": list(by_supplier), "grand_total": qs.aggregate(t=Sum("total_amount"))["t"] or 0})


class AccountsPayableReportView(APIView):
    def get(self, request):
        overdue = PaymentRequest.objects.filter(
            status=PaymentRequest.STATUS_PENDING,
            due_date__lt=date.today()
        ).select_related("invoice__supplier")
        pending = PaymentRequest.objects.filter(status=PaymentRequest.STATUS_PENDING)
        return Response({
            "total_pending": pending.count(),
            "total_amount_pending": pending.aggregate(t=Sum("amount"))["t"] or 0,
            "overdue_count": overdue.count(),
            "overdue_amount": overdue.aggregate(t=Sum("amount"))["t"] or 0,
        })


class DashboardView(APIView):
    permission_classes = [IsApprover]

    def get(self, request):
        return Response({
            "total_pr_pending": PurchaseRequisition.objects.filter(status="pending").count(),
            "total_ipo_pending_approval": IPO.objects.filter(status=IPO.STATUS_PENDING).count(),
            "total_active_orders": PurchaseOrder.objects.filter(
                status__in=["in_progress", "quotation_sent", "ipo_approved"]
            ).count(),
            "total_payment_pending": PaymentRequest.objects.filter(status="pending").count(),
            "monthly_spend": list(
                Invoice.objects.filter(status=Invoice.STATUS_PAID)
                .annotate(month=TruncMonth("invoice_date"))
                .values("month")
                .annotate(total=Sum("total_amount"))
                .order_by("-month")[:12]
            ),
        })


class ExportPOReportView(APIView):
    """Export PO status report to Excel."""

    def get(self, request):
        import openpyxl
        from django.http import HttpResponse
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "PO Report"
        headers = ["Order Number", "Status", "Created By", "Created At", "Notes"]
        ws.append(headers)
        for order in PurchaseOrder.objects.select_related("created_by").all()[:1000]:
            ws.append([
                order.order_number,
                order.get_status_display(),
                order.created_by.full_name,
                order.created_at.strftime("%d/%m/%Y"),
                order.notes or "",
            ])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        response = HttpResponse(
            buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="po_report.xlsx"'
        return response
