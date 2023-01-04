from datetime import datetime
from bson.objectid import ObjectId

from app.core.constants.employee_roles import EmployeeRole
from app.core.utilities.converter import str_to_match_all_regex
from ...core.utilities.database import db, default_find_limit


async def find_employees_by_filter(
        name: str | None = None, phone_number: str | None = None, roles: list[EmployeeRole] = [],
        is_active: bool | None = None, limit: int = default_find_limit, skip: int = 0
) -> list[dict]:
    filter = {}

    if name:
        filter["$or"] = [
            {"first_name": {"$regex": str_to_match_all_regex(s=name)}},
            {"last_name": {"$regex": str_to_match_all_regex(s=name)}}
        ]

    if phone_number:
        filter["phone_number"] = {
            "$regex": str_to_match_all_regex(s=phone_number)
        }

    if roles:
        filter["roles"] = {"$in": roles}

    if type(is_active) == bool:
        filter["is_active"] = is_active

    employees = [employee async for employee in db["employees"].find(filter=filter)]

    return list(employees) if employees else []


async def find_employee_by_id(id: str) -> dict:
    employee = await db["employees"].find_one(filter={"_id": ObjectId(id)})
    return dict(employee) if employee else {}


async def find_employee_by_phone_number(phone_number: str) -> dict:
    employee = await db["employees"].find_one(filter={"phone_number": phone_number})
    return dict(employee) if employee else {}


async def update_employee_password(id: str, new_password: str, updated_by: str) -> bool:
    update_result = await db["employees"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                "password": new_password,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by
            }
        }
    )

    if update_result.modified_count > 0:
        return True

    return False


async def update_employee_info(id: str, new_password: str, updated_by: str) -> bool:
    pass


async def push_to_employee_roles(id: str, roles: set[EmployeeRole], updated_by: str) -> bool:
    pass


async def pull_from_employee_roles(id: str, roles: set[EmployeeRole], updated_by: str) -> bool:
    pass


async def deactivate_employee(id: str, updated_by: str) -> bool:
    pass
