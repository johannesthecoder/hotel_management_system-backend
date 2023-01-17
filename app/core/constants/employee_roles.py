from enum import Enum


class EmployeeRole(str, Enum):
    # roles related to employees
    MANAGE_EMPLOYEES = "manage employees"
    VIEW_EMPLOYEES = "view employees"

    # roles related to customers
    MANAGE_CUSTOMERS = "manage customers"
    VIEW_CUSTOMERS = "view customers"

    # roles related to restaurant
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
    MANAGE_MENU_ITEMS = "manage menu items"

    # roles related to inventory
    MAKE_PURCHASE = "make purchase"
    VIEW_INVENTORY_ITEMS = "view inventory items"
    ISSUE_ITEM_TO_KITCHEN = "issue item to kitchen"
    UPDATE_PURCHASE = "update purchase"
    UPDATE_ISSUE_ITEM_TO_KITCHEN = "update issue item to kitchen"
    GENERATE_MY_INVENTORY_REPORT = "generate my inventory report"
    GENERATE_ALL_INVENTORY_REPORT = "generate all inventory report"
    MANAGE_INVENTORY_ITEMS = "manage inventory items"

    # roles related to inventory and restaurant
    MANAGE_RESTAURANT_PRODUCTION_COSTING = (
        "manage restaurant production costing"
    )


class RoleTemplate:
    waiter = [
        EmployeeRole.POST_ORDER,
        EmployeeRole.VIEW_MY_ORDERS,
        EmployeeRole.GENERATE_MY_SALES_REPORT,
    ]
    cashier = [
        EmployeeRole.VIEW_ALL_ORDERS,
        EmployeeRole.SETTLE_ORDER,
        EmployeeRole.TRANSFER_ORDER,
        EmployeeRole.GENERATE_ALL_SALES_REPORT,
    ]
    chef = [
        EmployeeRole.VIEW_ALL_ORDERS,
        EmployeeRole.VIEW_INVENTORY_ITEMS,
    ]
    inventorykeeper = [
        EmployeeRole.MAKE_PURCHASE,
        EmployeeRole.VIEW_INVENTORY_ITEMS,
        EmployeeRole.ISSUE_ITEM_TO_KITCHEN,
        EmployeeRole.UPDATE_PURCHASE,
        EmployeeRole.UPDATE_ISSUE_ITEM_TO_KITCHEN,
        EmployeeRole.GENERATE_MY_INVENTORY_REPORT,
        EmployeeRole.GENERATE_ALL_INVENTORY_REPORT,
        EmployeeRole.MANAGE_INVENTORY_ITEMS,
        EmployeeRole.MANAGE_RESTAURANT_PRODUCTION_COSTING,
    ]
    restaurant_supervisor = [
        EmployeeRole.POST_ORDER,
        EmployeeRole.VIEW_MY_ORDERS,
        EmployeeRole.VIEW_ALL_ORDERS,
        EmployeeRole.UPDATE_ORDER,
        EmployeeRole.VOID_ORDER,
        EmployeeRole.GIFT_ORDER,
        EmployeeRole.SETTLE_ORDER,
        EmployeeRole.TRANSFER_ORDER,
        EmployeeRole.GENERATE_MY_SALES_REPORT,
        EmployeeRole.GENERATE_ALL_SALES_REPORT,
        *inventorykeeper,
    ]
