"""Application-wide constants."""

# Supported currencies
SUPPORTED_CURRENCIES = ["SAR", "USD", "EUR", "AED", "KWD", "BHD", "OMR", "QAR"]

# Default VAT rate (Saudi Arabia)
DEFAULT_VAT_RATE = 15.0

# Invoice statuses
class InvoiceStatus:
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    ALL = [DRAFT, PENDING, PAID, PARTIALLY_PAID, OVERDUE, CANCELLED, REFUNDED]


# Stock movement types
class StockMovementType:
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"
    RETURN = "return"
    DAMAGE = "damage"

    ALL = [PURCHASE, SALE, ADJUSTMENT, TRANSFER, RETURN, DAMAGE]


# Payment methods
class PaymentMethod:
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CHEQUE = "cheque"
    ONLINE = "online"

    ALL = [CASH, BANK_TRANSFER, CREDIT_CARD, DEBIT_CARD, CHEQUE, ONLINE]


# Business types
BUSINESS_TYPES = [
    "retail",
    "wholesale",
    "manufacturing",
    "services",
    "restaurant",
    "pharmacy",
    "electronics",
    "fashion",
    "construction",
    "other",
]

# Pagination defaults
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
