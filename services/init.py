# services/__init__.py
from .order_service import create_order, get_order_by_id, update_order_status, calculate_order_total
from .customer_service import save_customer, get_customer, get_all_customers, update_customer_stats
from .billing_service import generate_bill, get_bill_by_order_id
from .promotion_service import send_promotion_to_all, save_promotion, get_all_promotions
from .message_service import save_message, get_message_history
from .admin_service import get_admin_stats
