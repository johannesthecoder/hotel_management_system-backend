from enum import Enum


class EmployeeRole(Enum):
    # roles related restaurant
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

    # roles related to store
    MAKE_PURCHASE = "make purchase"
    VIEW_STORE_ITEMS = "view store items"
    ISSUE_ITEM_TO_KITCHEN = "issue item to kitchen"
    UPDATE_PURCHASE = "update purchase"
    UPDATE_ISSUE_ITEM_TO_KITCHEN = "update issue item to kitchen"
    GENERATE_MY_STORE_REPORT = "generate my store report"
    GENERATE_ALL_STORE_REPORT = "generate all store report"
    MANAGE_STORE_ITEMS = "manage store items"

    # roles related to store and restaurant
    MANAGE_RESTAURANT_PRODUCTION_COSTING = "manage restaurant production costing"


class RoleTemplate:
    waiter = [
        EmployeeRole.POST_ORDER, EmployeeRole.VIEW_MY_ORDERS,
        EmployeeRole.GENERATE_MY_SALES_REPORT,
    ]
    cashier = [
        EmployeeRole.VIEW_ALL_ORDERS, EmployeeRole.SETTLE_ORDER,
        EmployeeRole.TRANSFER_ORDER, EmployeeRole.GENERATE_ALL_SALES_REPORT,
    ]
    chef = [EmployeeRole.VIEW_ALL_ORDERS, EmployeeRole.VIEW_STORE_ITEMS,]
    storekeeper = [
        EmployeeRole.MAKE_PURCHASE, EmployeeRole.VIEW_STORE_ITEMS,
        EmployeeRole.ISSUE_ITEM_TO_KITCHEN, EmployeeRole.UPDATE_PURCHASE,
        EmployeeRole.UPDATE_ISSUE_ITEM_TO_KITCHEN,
        EmployeeRole.GENERATE_MY_STORE_REPORT, EmployeeRole.GENERATE_ALL_STORE_REPORT,
        EmployeeRole.MANAGE_STORE_ITEMS,
        EmployeeRole.MANAGE_RESTAURANT_PRODUCTION_COSTING,
    ]
    restaurant_supervisor = [
        EmployeeRole.POST_ORDER, EmployeeRole.VIEW_MY_ORDERS,
        EmployeeRole.VIEW_ALL_ORDERS, EmployeeRole.UPDATE_ORDER,
        EmployeeRole.VOID_ORDER, EmployeeRole.GIFT_ORDER,
        EmployeeRole.SETTLE_ORDER, EmployeeRole.TRANSFER_ORDER,
        EmployeeRole.GENERATE_MY_SALES_REPORT, EmployeeRole.GENERATE_ALL_SALES_REPORT,
        *storekeeper,
    ]
