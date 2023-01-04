from bson.objectid import ObjectId
from ...core.utilities.database import db


async def employee_exist(phone_number: str) -> bool:
    if await db["employees"].count_documents({"phone_number": phone_number}) > 0:
        return True
    return False


async def insert_employee(employee: dict) -> str | None:
    return await db["employees"].insert_one(employee)


async def find_employee_by_phone_number(phone_number: str) -> dict:
    employee = await db["employees"].find_one(filter={"phone_number": phone_number})
    return dict(employee) if employee else {}


async def find_employee_by_id(id: str) -> dict:
    employee = await db["employees"].find_one(filter={"_id": ObjectId(id)})
    return dict(employee) if employee else {}


async def update_employee_password(id: str, new_password: str) -> bool:
    update_result = await db["employees"].update_one(
        filter={"_id": ObjectId(id)},
        update={"$set": {"password": new_password}}
    )

    if update_result.modified_count > 0:
        return True

    return False
