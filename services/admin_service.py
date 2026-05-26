# services/admin_service.py
from services.order_service import read_json as read_orders
from services.customer_service import get_all_customers
from services.billing_service import get_all_bills
from services.message_service import get_all_messages
from services.promotion_service import get_all_promotions
from debug_logger import log

def get_admin_stats():
    """Get admin dashboard statistics"""
    orders = read_orders("orders.json")
    customers = get_all_customers()
    bills = get_all_bills()
    messages = get_all_messages()
    promotions = get_all_promotions()
    
    # Calculate total revenue
    total_revenue = sum(bill.get("total", 0) for bill in bills)
    
    # Calculate average order value
    avg_order_value = total_revenue / len(orders) if orders else 0
    
    # Count orders by status
    order_status_count = {}
    for order in orders:
        status = order.get("status", "unknown")
        order_status_count[status] = order_status_count.get(status, 0) + 1
    
    return {
        "total_orders": len(orders),
        "total_customers": len(customers),
        "total_revenue": total_revenue,
        "avg_order_value": round(avg_order_value, 2),
        "total_messages": len(messages),
        "total_promotions": len(promotions),
        "order_status_count": order_status_count,
        "recent_orders": orders[-10:],
        "recent_customers": customers[-10:]
    }
