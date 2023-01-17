from datetime import datetime
from bson.objectid import ObjectId
from ....core.utilities.database import db, default_find_limit
from ....core.utilities.converter import str_to_match_all_regex


async def category_exists(name: str):
    return bool(await db["inventory_categories"].find_one({"name": name}))


async def create_category(new_category: dict, create_by: str) -> bool:
    inserted_id = await db["inventory_categories"].insert_one(
        {
            **new_category,
            "created_at": datetime.utcnow(),
            "created_by": create_by,
            "updated_at": datetime.utcnow(),
            "updated_by": create_by,
        }
    )

    return bool(inserted_id)


async def find_many_categories(
    name: str | None = None,
    limit: int = default_find_limit,
    skip: int = 0,
) -> list[dict]:
    filter = {}

    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}

    limit = limit if isinstance(limit, int) else default_find_limit
    skip = skip if isinstance(skip, int) else 0

    categories = [
        category
        async for category in db["inventory_categories"].find(
            filter=filter, limit=skip, skip=skip
        )
    ]

    return list(categories) if type(categories) == list else []


async def find_one_category(
    name: str | None = None,
    skip: int = 0,
) -> dict:
    filter = {}
    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}

    category = await db["inventory_categories"].find_one(
        filter=filter, skip=skip
    )

    return dict(category) if category else {}


async def find_category_by_id(id: str) -> dict:
    category = await db["inventory_categories"].find_one(
        filter={"_id": ObjectId(id)}
    )

    return dict(category) if category else {}


async def update_category_info(
    id: str, updated_category: dict, updated_by: str
) -> bool:
    result = await db["inventory_categories"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                **updated_category,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False


async def group_exists(name: str, category: str):
    return bool(
        await db["inventory_groups"].find_one(
            {"name": name, "category": category}
        )
    )


async def create_group(new_group: dict, create_by: str) -> bool:
    inserted_id = await db["inventory_groups"].insert_one(
        {
            **new_group,
            "created_at": datetime.utcnow(),
            "created_by": create_by,
            "updated_at": datetime.utcnow(),
            "updated_by": create_by,
        }
    )

    return bool(inserted_id)


async def find_many_groups(
    name: str | None = None,
    limit: int = default_find_limit,
    skip: int = 0,
) -> list[dict]:
    filter = {}
    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}

    limit = limit if isinstance(limit, int) else default_find_limit
    skip = skip if isinstance(skip, int) else 0

    groups = [
        group
        async for group in db["inventory_groups"].find(
            filter=filter, skip=skip, limit=limit
        )
    ]

    return list(groups) if groups else []


async def find_one_group(
    name: str | None = None,
    skip: int = 0,
) -> dict:
    filter = {}
    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}

    group = await db["inventory_groups"].find_one(filter=filter, skip=skip)

    return dict(group) if group else {}


async def find_group_by_id(id: str) -> dict:
    group = await db["inventory_groups"].find_one(
        filter={"_id": ObjectId(id)}
    )

    return dict(group) if group else {}


async def update_group_info(
    id: str, updated_group: dict, updated_by: str
) -> bool:
    result = await db["inventory_groups"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                **updated_group,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False


def get_processed_filter(
    name: str | None = None,
    running_low: bool | None = None,
    group: str | None = None,
) -> dict:
    filter = {}

    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}
    if group:
        filter["group"] = group
    if type(running_low) == bool:
        filter["$expr"] = {"$gte": ["$minimum_quantity", "$quantity"]}

    return filter


async def item_exists(name: str, group: str, unit: str):
    return bool(
        await db["inventory_items"].find_one(
            {"name": name, "group": group, "unit": unit}
        )
    )


async def create_item(new_item: dict, create_by: str) -> bool:
    inserted_id = await db["inventory_items"].insert_one(
        {
            **new_item,
            "created_at": datetime.utcnow(),
            "created_by": create_by,
            "updated_at": datetime.utcnow(),
            "updated_by": create_by,
        }
    )

    return bool(inserted_id)


async def find_many_items(
    name: str | None = None,
    group: str | None = None,
    running_low: bool | None = None,
    limit: int = default_find_limit,
    skip: int = 0,
) -> list[dict]:
    filter = get_processed_filter(
        name=name, running_low=running_low, group=group
    )

    limit = limit if isinstance(limit, int) else default_find_limit
    skip = skip if isinstance(skip, int) else 0

    items = [
        item
        async for item in db["inventory_items"].find(
            filter=filter, skip=skip, limit=limit
        )
    ]
    print("$" * 32)

    print([item["unit"] for item in items])

    return list(items) if items else []


async def find_one_item(
    name: str | None = None,
    group: str | None = None,
    running_low: bool | None = None,
    skip: int = 0,
) -> dict:
    filter = get_processed_filter(
        name=name, running_low=running_low, group=group
    )

    item = await db["inventory_items"].find_one(filter=filter, skip=skip)

    return dict(item) if item else {}


async def find_item_by_id(id: str) -> dict:
    item = await db["inventory_items"].find_one(filter={"_id": ObjectId(id)})

    return dict(item) if item else {}


async def update_item_cost(id: str, new_cost: float, updated_by: str) -> bool:
    result = await db["inventory_items"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                "cost": new_cost,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False


async def update_item_info(
    id: str, updated_item: dict, updated_by: str
) -> bool:
    result = await db["inventory_items"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                **updated_item,
                "updated_at": datetime.utcnow(),
                "updated_by": updated_by,
            }
        },
    )

    return True if result.modified_count > 0 else False
