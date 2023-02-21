from datetime import datetime
from bson.objectid import ObjectId
from ....core.utilities.database import default_find_limit
from ....core.utilities.database import db


def get_processed_filter(
    item: str,
    issued_by: str,
    issued_at_from: datetime,
    issued_at_to: datetime,
):
    filter = {}
    if item:
        filter["item"] = (item,)

    if issued_by:
        filter["issued_by"] = issued_by

    if issued_at_from or issued_at_from:
        filter["issued_at"] = {}

        if issued_at_from:
            filter["issued_at"]["$gte"] = issued_at_from

        if issued_at_to:
            filter["issued_at"]["$lte"] = issued_at_to

    return filter


def get_processed_sort(sort_by: list[str]) -> dict:
    sort_dict = {}

    for sort_item in sort_by:
        if sort_item[0] in "+-":
            sort_dict[sort_item[1:]] = 1 if sort_item[0] == "+" else "-"


async def issue_item(new_issue: dict, issued_by: str) -> str | None:
    inserted_issue = await db["inventory_issues"].insert_one(
        {
            **new_issue,
            "issued_by": issued_by,
            "updated_at": datetime.utcnow(),
            "updated_by": issued_by,
        }
    )

    return inserted_issue.inserted_id


async def find_many_issues(
    item: str | None = None,
    issued_by: str | None = None,
    issued_at_from: datetime | None = None,
    issued_at_to: datetime | None = None,
    limit: int = 0,
    skip: int = 0,
    sort_by: list[str] = [],
) -> list[dict]:
    filter = get_processed_filter(
        item=item,
        issued_by=issued_by,
        issued_at_from=issued_at_from,
        issued_at_to=issued_at_to,
    )
    sort = get_processed_sort(sort_by=sort_by)

    issues = [
        issue
        async for issue in db["inventory_issues"].find(
            filter=filter,
            skip=skip,
            limit=limit if limit > 0 else default_find_limit,
            sort=sort,
        )
    ]

    return issues


async def find_one_issue(
    item: str,
    received_by: str,
    issued_by: str,
    receiver_accepted: bool,
    issued_at_from: datetime,
    issued_at_to: datetime,
    skip: int = 0,
) -> dict:
    filter = get_processed_filter(
        item=item,
        received_by=received_by,
        issued_by=issued_by,
        receiver_accepted=receiver_accepted,
        issued_at_from=issued_at_from,
        issued_at_to=issued_at_to,
    )

    issue = await db["inventory_issues"].find_one(filter=filter, skip=skip)

    return dict(issue) if issue else {}


async def find_issue_by_id(id: str) -> dict:
    issue = await db["inventory_issues"].find_one(
        filter={"_id": ObjectId(id)}
    )

    return dict(issue) if issue else {}


async def update_issue(id: str, updated_issue: dict, updated_by: str) -> bool:
    result = await db["inventory_issues"].update_one(
        filter={"_id": ObjectId(id)},
        update={
            "$set": {
                **updated_issue,
                "updated_by": updated_by,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return True if result.modified_count > 0 else False
