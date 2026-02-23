"""
constants.py - Business constants and enumerations for the Jenan-Biz application.
"""

import enum


class UserRole(str, enum.Enum):
    """User roles within the system."""

    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    OPERATOR = "operator"


class CustomerType(str, enum.Enum):
    """Customer classification types."""

    RETAIL = "retail"
    WHOLESALE = "wholesale"
    CORPORATE = "corporate"


class InvoiceStatus(str, enum.Enum):
    """Sales invoice lifecycle statuses."""

    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment completion statuses."""

    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class PurchaseInvoiceStatus(str, enum.Enum):
    """Purchase invoice lifecycle statuses."""

    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ReceiptStatus(str, enum.Enum):
    """Goods receipt statuses for purchase invoices."""

    PENDING = "pending"
    PARTIALLY_RECEIVED = "partially_received"
    FULLY_RECEIVED = "fully_received"


class StockStatus(str, enum.Enum):
    """Inventory stock level statuses."""

    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


# Tax rate applied to invoices (15%)
TAX_RATE: float = 0.15

# Invoice number format prefixes
SALES_INVOICE_PREFIX: str = "INV"
PURCHASE_INVOICE_PREFIX: str = "PUR"
