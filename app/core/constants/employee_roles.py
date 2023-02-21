from enum import Enum


class EmployeeRole(str, Enum):
    # roles related to account
    # roles related to account.employees
    MANAGE_EMPLOYEES = "manage employees"
    VIEW_EMPLOYEES = "view employees"

    # roles related to account.customers
    MANAGE_CUSTOMERS = "manage customers"
    VIEW_CUSTOMERS = "view customers"

    # roles related to restaurant

    ## roles related to restaurant.menu
    MANAGE_MENU_ITEMS = "manage menu items"
    VIEW_MENU_ITEMS = "manage menu items"
    UPDATE_MENU_ITEMS = "manage menu items"

    ## roles related to restaurant.orders
    POST_ORDER = "post order"
    VIEW_MY_ORDERS = "view my orders"
    VIEW_ALL_ORDERS = "view all orders"
    UPDATE_ORDER = "update order"
    VOID_ORDER = "void order"
    GIFT_ORDER = "gift order"
    SETTLE_ORDER = "settle order"
    TRANSFER_ORDER = "transfer order"
    GENERATE_MY_SALES_REPORT = "generate my sales report"
    GENERATE_ALL_SALES_REPORT = "generate all sales report"

    # roles related to inventory

    ## roles related to inventory.items
    MANAGE_INVENTORY_ITEMS = "manage inventory items"
    VIEW_INVENTORY_ITEMS = "view inventory items"
    GENERATE_INVENTORY_REPORT = "generate my inventory report"

    ## roles related to inventory.issues
    ISSUE = "issue"
    VIEW_ISSUE = "view issue"
    UPDATE_ISSUE = "update issue"

    ## roles related to inventory.purchases
    PURCHASE = "purchase"
    VIEW_PURCHASE = "view purchase"
    UPDATE_PURCHASE = "update purchase"

    # roles related to kitchen
    MANAGE_KITCHEN = "manage kitchen"


# class RoleTemplate:
#     waiter = [
#         EmployeeRole.POST_ORDER,
#         EmployeeRole.VIEW_MY_ORDERS,
#         EmployeeRole.GENERATE_MY_SALES_REPORT,
#     ]
#     cashier = [
#         EmployeeRole.VIEW_ALL_ORDERS,
#         EmployeeRole.SETTLE_ORDER,
#         EmployeeRole.TRANSFER_ORDER,
#         EmployeeRole.GENERATE_ALL_SALES_REPORT,
#     ]
#     chef = [
#         EmployeeRole.VIEW_ALL_ORDERS,
#         EmployeeRole.VIEW_INVENTORY_ITEMS,
#     ]
#     storekeeper = [
#         EmployeeRole.MAKE_PURCHASE,
#         EmployeeRole.VIEW_INVENTORY_ITEMS,
#         EmployeeRole.ISSUE,
#         EmployeeRole.UPDATE_PURCHASE,
#         EmployeeRole.UPDATE_ISSUE,
#         EmployeeRole.GENERATE_MY_INVENTORY_REPORT,
#         EmployeeRole.GENERATE_ALL_INVENTORY_REPORT,
#         EmployeeRole.MANAGE_INVENTORY_ITEMS,
#         EmployeeRole.MANAGE_RESTAURANT_PRODUCTION_COSTING,
#     ]
#     restaurant_supervisor = [
#         EmployeeRole.POST_ORDER,
#         EmployeeRole.VIEW_MY_ORDERS,
#         EmployeeRole.VIEW_ALL_ORDERS,
#         EmployeeRole.UPDATE_ORDER,
#         EmployeeRole.VOID_ORDER,
#         EmployeeRole.GIFT_ORDER,
#         EmployeeRole.SETTLE_ORDER,
#         EmployeeRole.TRANSFER_ORDER,
#         EmployeeRole.GENERATE_MY_SALES_REPORT,
#         EmployeeRole.GENERATE_ALL_SALES_REPORT,
#         *storekeeper,
#     ]
