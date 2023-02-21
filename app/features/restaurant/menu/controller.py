from datetime import datetime
from bson.objectid import ObjectId
from ....core.utilities.database import db, default_find_limit
from ....core.utilities.converter import str_to_match_all_regex


async def category_exists(name: str):
    return bool(await db["menu_categories"].find_one({"name": name}))


async def create_category(new_category: dict, create_by: str) -> bool:
    inserted_id = await db["menu_categories"].insert_one(
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
    limit: int = 0,
    skip: int = 0,
) -> list[dict]:
    filter = {}

    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}

    categories = [
        category
        async for category in db["menu_categories"].find(
            filter=filter,
            skip=skip,
            limit=limit if limit > 0 else default_find_limit,
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

    category = await db["menu_categories"].find_one(filter=filter, skip=skip)

    return dict(category) if category else {}


async def find_category_by_id(id: str) -> dict:
    category = await db["menu_categories"].find_one(
        filter={"_id": ObjectId(id)}
    )

    return dict(category) if category else {}


async def update_category_info(
    id: str, updated_category: dict, updated_by: str
) -> bool:
    result = await db["menu_categories"].update_one(
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
        await db["menu_groups"].find_one({"name": name, "category": category})
    )


async def create_group(new_group: dict, create_by: str) -> bool:
    inserted_id = await db["menu_groups"].insert_one(
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
    limit: int = 0,
    skip: int = 0,
) -> list[dict]:
    filter = {}
    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}

    groups = [
        group
        async for group in db["menu_groups"].find(
            filter=filter,
            skip=skip,
            limit=limit if limit > 0 else default_find_limit,
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

    group = await db["menu_groups"].find_one(filter=filter, skip=skip)

    return dict(group) if group else {}


async def find_group_by_id(id: str) -> dict:
    group = await db["menu_groups"].find_one(filter={"_id": ObjectId(id)})

    return dict(group) if group else {}


async def update_group_info(
    id: str, updated_group: dict, updated_by: str
) -> bool:
    result = await db["menu_groups"].update_one(
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
    group: str | None = None,
) -> dict:
    filter = {}

    if name:
        filter["name"] = {"$regex": str_to_match_all_regex(s=name)}
    if group:
        filter["group"] = group

    return filter


def get_processed_sort(sort_by: list[str]) -> dict:
    sort_dict = {}

    for sort_item in sort_by:
        if sort_item[0] in "+-":
            sort_dict[sort_item[1:]] = 1 if sort_item[0] == "+" else "-"


async def item_exists(name: str, group: str):
    return bool(
        await db["menu_items"].find_one({"name": name, "group": group})
    )


async def create_item(new_item: dict, create_by: str) -> bool:
    inserted_id = await db["menu_items"].insert_one(
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
    limit: int = 0,
    skip: int = 0,
    sort_by: list[str] = [],
) -> list[dict]:
    filter = get_processed_filter(name=name, group=group)
    sort = get_processed_sort(sort_by=sort_by)

    items = [
        item
        async for item in db["menu_items"].find(
            filter=filter,
            skip=skip,
            limit=limit if limit > 0 else default_find_limit,
            sort=sort,
        )
    ]

    return list(items) if items else []


async def find_one_item(
    name: str | None = None,
    group: str | None = None,
    skip: int = 0,
) -> dict:
    filter = get_processed_filter(name=name, group=group)

    item = await db["menu_items"].find_one(filter=filter, skip=skip)

    return dict(item) if item else {}


async def find_item_by_id(id: str) -> dict:
    item = await db["menu_items"].find_one(filter={"_id": ObjectId(id)})

    return dict(item) if item else {}


async def update_item_info(
    id: str, updated_item: dict, updated_by: str
) -> bool:
    result = await db["menu_items"].update_one(
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


async def add_item_accompaniments(
    id: str, accompaniments: list[str], updated_by
):
    result = await db["menu_items"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$addToSet": {"accompaniments": {"$each": accompaniments}},
            "$set": {
                "updated_by": updated_by,
                "updated_at": datetime.utcnow(),
            },
        },
    )

    return True if result.modified_count > 0 else False


async def remove_item_accompaniments(
    id: str, accompaniments: list[str], updated_by
):
    result = await db["menu_items"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$pull": {"accompaniments": {"$in": accompaniments}},
            "$set": {
                "updated_by": updated_by,
                "updated_at": datetime.utcnow(),
            },
        },
    )

    return True if result.modified_count > 0 else False
