"""
Shared Utilities - Common helper functions
"""
from datetime import datetime, date
from typing import Optional, Any
import uuid
import re


def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())


def generate_number(prefix: str, sequence: int, year: Optional[int] = None) -> str:
    """
    Generate a formatted number (e.g., for invoices, orders)
    Example: INV-2024-00001
    """
    if year is None:
        year = datetime.now().year
    return f"{prefix}-{year}-{sequence:05d}"


def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format amount as currency string"""
    if currency == "EUR":
        return f"{amount:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{amount:,.2f} {currency}"


def parse_decimal(value: Any) -> float:
    """Parse string or number to float"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Handle German number format
        value = value.replace(".", "").replace(",", ".")
        value = re.sub(r"[^\d.-]", "", value)
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def calculate_tax(net_amount: float, tax_rate: float = 19.0) -> tuple:
    """
    Calculate tax amount and gross amount
    Returns: (tax_amount, gross_amount)
    """
    tax_amount = net_amount * (tax_rate / 100)
    gross_amount = net_amount + tax_amount
    return (round(tax_amount, 2), round(gross_amount, 2))


def calculate_net(gross_amount: float, tax_rate: float = 19.0) -> tuple:
    """
    Calculate net amount and tax from gross
    Returns: (net_amount, tax_amount)
    """
    net_amount = gross_amount / (1 + tax_rate / 100)
    tax_amount = gross_amount - net_amount
    return (round(net_amount, 2), round(tax_amount, 2))


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:195] + ("." + ext if ext else "")
    return filename


def format_date_german(dt: date) -> str:
    """Format date in German format"""
    if dt is None:
        return ""
    return dt.strftime("%d.%m.%Y")


def format_datetime_german(dt: datetime) -> str:
    """Format datetime in German format"""
    if dt is None:
        return ""
    return dt.strftime("%d.%m.%Y %H:%M")


def slugify(text: str) -> str:
    """Create a URL-friendly slug from text"""
    text = text.lower()
    # Replace umlauts
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove special chars
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    # Replace spaces with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove multiple hyphens
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


class Pagination:
    """Helper class for pagination"""
    
    def __init__(self, page: int = 1, per_page: int = 20, total: int = 0):
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), 100)
        self.total = total
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def total_pages(self) -> int:
        if self.total == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev
        }
