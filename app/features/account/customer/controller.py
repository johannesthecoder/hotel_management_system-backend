from datetime import datetime
from bson.objectid import ObjectId
from ....core.utilities.database import db, default_find_limit
from ....core.utilities.converter import str_to_match_all_regex


def get_processed_filter(
    name: str | None = None,
    phone_number: str | None = None,
    roles: list[str] = [],
    is_active: bool | None = None,
) -> dict:
    filter = {}

    if name:
        filter["$or"] = [
            {"first_name": {"$regex": str_to_match_all_regex(s=name)}},
            {"last_name": {"$regex": str_to_match_all_regex(s=name)}},
        ]
    if phone_number:
        filter["phone_number"] = {
            "$regex": str_to_match_all_regex(s=phone_number)
        }
    if roles:
        filter["roles"] = {"$in": roles}
    if type(is_active) == bool:
        filter["is_active"] = is_active

    return filter


async def create_customer(new_customer: dict, create_by: str) -> bool:
    inserted_id = await db["customers"].insert_one(
        {
            **new_customer,
            "created_at": datetime.utcnow(),
            "created_by": create_by,
            "updated_at": datetime.utcnow(),
            "updated_by": create_by,
        }
    )

    return bool(inserted_id)


async def find_many_customers(
    roles: list[str] = [],
    limit: int | None = None,
    skip: int | None = None,
    name: str | None = None,
    phone_number: str | None = None,
    is_active: bool | None = None,
) -> list[dict]:
    filter = get_processed_filter(
        name=name, phone_number=phone_number, is_active=is_active, roles=roles
    )

    limit = limit if isinstance(limit, int) else default_find_limit
    skip = skip if isinstance(skip, int) else 0

    customers = [
        customer
        async for customer in db["customers"]
        .find(filter=filter)
        .limit(limit)
        .skip(skip)
    ]

    return list(customers) if customers else []


async def find_one_customer(
    name: str | None = None,
    phone_number: str | None = None,
    roles: list[str] = [],
    is_active: bool | None = None,
    limit: int = default_find_limit,
    skip: int = 0,
) -> dict:
    filter = get_processed_filter(
        name=name, phone_number=phone_number, is_active=is_active, roles=roles
    )

    customer = await db["customers"].find_one(filter=filter)

    return dict(customer) if customer else {}


async def find_customer_by_id(id: str) -> dict:
    customer = await db["customers"].find_one(filter={"_id": ObjectId(id)})

    return dict(customer) if customer else {}


async def find_customer_by_phone_number(phone_number: str) -> dict:
    customer = await db["customers"].find_one(
        filter={"phone_number": phone_number}
    )

    return dict(customer) if customer else {}


async def update_customer_password(
    id: str, new_password: str, updated_by: str
) -> bool:
    result = await db["customers"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                "password": new_password,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False


async def deactivate_customer(id: str, updated_by: str) -> bool:
    result = await db["customers"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False


async def activate_customer(id: str, updated_by: str) -> bool:
    result = await db["customers"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                "is_active": True,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False


async def update_customer_info(
    id: str, updated_customer: dict, updated_by: str
) -> bool:
    result = await db["customers"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                **updated_customer,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False
