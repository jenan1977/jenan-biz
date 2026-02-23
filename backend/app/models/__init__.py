"""
Models package - imports all models to ensure they are registered with SQLAlchemy.
"""

from app.models.base import Base
from app.models.company import Company
from app.models.user import User
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.sales_invoice import SalesInvoice
from app.models.sales_line_item import SalesLineItem
from app.models.purchase_invoice import PurchaseInvoice
from app.models.purchase_line_item import PurchaseLineItem
from app.models.inventory import Inventory
from app.models.job import Job

# Blog module models
from app.blog.models import (  # noqa: F401
    Article,
    ArticleCategory,
    ArticleComment,
    ArticleRating,
    ArticleTag,
    article_tag_map,
)

__all__ = [
    "Base",
    "Company",
    "User",
    "Customer",
    "Supplier",
    "Product",
    "SalesInvoice",
    "SalesLineItem",
    "PurchaseInvoice",
    "PurchaseLineItem",
    "Inventory",
    "Job",
    # Blog
    "Article",
    "ArticleCategory",
    "ArticleComment",
    "ArticleRating",
    "ArticleTag",
    "article_tag_map",
]
