from datetime import datetime
from bson.objectid import ObjectId
from ....core.utilities.database import default_find_limit
from ....core.utilities.database import db


def get_processed_filter(
    item: str,
    purchased_by: str,
    purchased_at_from: datetime,
    purchased_at_to: datetime,
):
    filter = {}
    if item:
        filter["item"] = (item,)

    if purchased_by:
        filter["purchased_by"] = purchased_by

    if purchased_at_from or purchased_at_from:
        filter["purchased_at"] = {}

        if purchased_at_from:
            filter["purchased_at"]["$gte"] = purchased_at_from

        if purchased_at_to:
            filter["purchased_at"]["$lte"] = purchased_at_to

    return filter


async def purchase_item(new_purchase: dict, purchased_by: str) -> str | None:
    inserted_purchase = await db["inventory_purchases"].insert_one(
        {
            **new_purchase,
            "purchased_by": purchased_by,
            "updated_at": datetime.utcnow(),
            "updated_by": purchased_by,
        }
    )

    return inserted_purchase.inserted_id


async def find_many_purchases(
    item: str | None = None,
    purchased_by: str | None = None,
    purchased_at_from: datetime | None = None,
    purchased_at_to: datetime | None = None,
    limit: int = default_find_limit,
    skip: int = 0,
) -> list[dict]:
    filter = get_processed_filter(
        item=item,
        purchased_by=purchased_by,
        purchased_at_from=purchased_at_from,
        purchased_at_to=purchased_at_to,
    )

    limit = limit if isinstance(limit, int) else default_find_limit
    skip = skip if isinstance(skip, int) else 0

    purchases = [
        purchase
        async for purchase in db["inventory_purchases"].find(
            filter=filter, skip=skip, limit=limit
        )
    ]

    return purchases


async def find_one_purchase(
    item: str,
    received_by: str,
    purchased_by: str,
    receiver_accepted: bool,
    purchased_at_from: datetime,
    purchased_at_to: datetime,
    skip: int = 0,
) -> dict:
    filter = get_processed_filter(
        item=item,
        received_by=received_by,
        purchased_by=purchased_by,
        receiver_accepted=receiver_accepted,
        purchased_at_from=purchased_at_from,
        purchased_at_to=purchased_at_to,
    )

    skip = skip if isinstance(skip, int) else 0

    purchase = await db["inventory_purchases"].find_one(
        filter=filter, skip=skip
    )

    return dict(purchase) if purchase else {}


async def find_purchase_by_id(id: str) -> dict:
    purchase = await db["inventory_purchases"].find_one(
        filter={"_id": ObjectId(id)}
    )

    return dict(purchase) if purchase else {}


async def update_purchase(
    id: str, updated_purchase: dict, updated_by: str
) -> bool:
    result = await db["inventory_purchases"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                **updated_purchase,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return True if result.modified_count > 0 else False
