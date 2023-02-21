from fastapi import APIRouter, Depends, Query

from bson.objectid import ObjectId
from app.core.constants.employee_roles import EmployeeRole
from app.core.utilities.converter import (
    dict_to_model,
    model_to_dict_without_None,
)
from ....core.utilities.jwt_config import AuthJWT, EmployeeRoleChecker
from app.core.error.exceptions import (
    raise_duplicated_entry_exception,
    raise_not_found_exception,
    raise_operation_failed_exception,
    raise_unprocessable_value_exception,
)
from . import models
from . import controller

menu_router = APIRouter()
category_router = APIRouter()
group_router = APIRouter()
item_router = APIRouter()
category_router.tags = ["Menu - Categories"]
group_router.tags = ["Menu - Groups"]
item_router.tags = ["Menu - Items"]


@category_router.post("/", response_model=models.SingleCategoryResponseModel)
async def create_category(
    new_category: models.CategoryBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    new_category.name = new_category.name.lower()
    if await controller.category_exists(name=new_category.name):
        raise_duplicated_entry_exception(
            message="this category already exists",
            location=["request body", "name"],
        )

    await controller.create_category(
        new_category=new_category.dict(), create_by=current_user_id
    )

    category = await controller.find_one_category(name=new_category.name)
    if not category:
        raise_operation_failed_exception(
            message="problem while creating menu category"
        )

    return models.SingleCategoryResponseModel(
        success=True,
        category=dict_to_model(
            model=models.CategoryReadModel,
            dict_model=category,
        ),
    )


@category_router.get(
    "/{category_id}", response_model=models.SingleCategoryResponseModel
)
async def get_category(
    category_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(category_id):
        raise_unprocessable_value_exception(
            message=f"invalid category_id={category_id}",
            location=["path parameter", "category_id"],
        )

    category = await controller.find_category_by_id(id=category_id)

    if not category:
        raise_not_found_exception(
            message=f"no category found with an id={category_id}",
            location=["path parameter", "category_id"],
        )

    return models.SingleCategoryResponseModel(
        success=True,
        category=dict_to_model(
            model=models.CategoryReadModel, dict_model=category
        ),
    )


@category_router.get(
    "/", response_model=models.MultipleCategoriesResponseModel
)
async def get_categories(
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_MENU_ITEMS)
    ),
):
    categories = await controller.find_many_categories()

    if not type(categories) == list:
        raise_operation_failed_exception(
            message="problem while getting menu category"
        )

    return models.MultipleCategoriesResponseModel(
        success=True,
        categories=[
            dict_to_model(
                model=models.CategoryReadModel,
                dict_model=category,
            )
            for category in categories
        ],
    )


@category_router.patch(
    "/{category_id}",
    response_model=models.SingleCategoryResponseModel,
)
async def update_category(
    category_id: str,
    updated_category: models.CategoryUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(category_id):
        raise_unprocessable_value_exception(
            message=f"invalid category_id={category_id}",
            location=["path parameter", "category_id"],
        )

    if updated_category.name:
        updated_category.name = updated_category.name.lower()

    if await controller.category_exists(name=updated_category.name):
        raise_duplicated_entry_exception(
            message="this category already exists",
            location=["request body", "name"],
        )

    result = await controller.update_category_info(
        id=category_id,
        updated_category=model_to_dict_without_None(model=updated_category),
        updated_by=current_user_id,
    )

    category = await controller.find_category_by_id(id=category_id)

    if not result or not category:
        raise_operation_failed_exception(
            message="problem while updating category"
        )

    return models.SingleCategoryResponseModel(
        success=True,
        category=dict_to_model(
            model=models.CategoryReadModel, dict_model=category
        ),
    )


@group_router.post("/", response_model=models.SingleGroupResponseModel)
async def create_groups(
    new_group: models.GroupBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(new_group.category):
        raise_unprocessable_value_exception(
            message=f"invalid category_id={new_group.category}",
            location=["request body", "category"],
        )

    if not await controller.find_category_by_id(id=new_group.category):
        raise_not_found_exception(
            message=f"no category was found with {new_group.category} id",
            location=["request body", "category"],
        )

    new_group.name = new_group.name.lower()

    if await controller.group_exists(
        name=new_group.name, category=new_group.category
    ):
        raise_duplicated_entry_exception(
            message="this group already exists",
            location=["request body", "name"],
        )

    await controller.create_group(
        new_group=new_group.dict(), create_by=current_user_id
    )

    group = await controller.find_one_group(name=new_group.name)
    if not group:
        raise_operation_failed_exception(
            message="problem while creating menu group"
        )

    return models.SingleGroupResponseModel(
        success=True,
        group=dict_to_model(
            model=models.GroupReadModel,
            dict_model=group,
        ),
    )


@group_router.get(
    "/{group_id}", response_model=models.SingleGroupResponseModel
)
async def get_group(
    group_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(group_id):
        raise_unprocessable_value_exception(
            message=f"invalid group_id={group_id}",
            location=["path parameter", "group_id"],
        )

    group = await controller.find_group_by_id(id=group_id)

    if not group:
        raise_not_found_exception(
            message=f"no group found with an id={group_id}",
            location=["path parameter", "group_id"],
        )

    return models.SingleGroupResponseModel(
        success=True,
        group=dict_to_model(model=models.GroupReadModel, dict_model=group),
    )


@group_router.get("/", response_model=models.MultipleGroupsResponseModel)
async def get_group(
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_MENU_ITEMS)
    ),
):
    groups = await controller.find_many_groups()

    if not type(groups) == list:
        raise_operation_failed_exception(
            message="problem while getting menu group"
        )

    return models.MultipleGroupsResponseModel(
        success=True,
        groups=[
            dict_to_model(
                model=models.GroupReadModel,
                dict_model=group,
            )
            for group in groups
        ],
    )


@group_router.patch(
    "/{group_id}",
    response_model=models.SingleGroupResponseModel,
)
async def update_group(
    group_id: str,
    updated_group: models.GroupUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(group_id):
        raise_unprocessable_value_exception(
            message=f"invalid group_id={group_id}",
            location=["path parameter", "group_id"],
        )
    if updated_group.category:
        if not ObjectId.is_valid(updated_group.category):
            raise_unprocessable_value_exception(
                message=f"invalid category_id={updated_group.category}",
                location=["path parameter", "category"],
            )

        if not await controller.find_category_by_id(
            id=updated_group.category
        ):
            raise_not_found_exception(
                message=f"no category was found with {updated_group.category} id",
                location=["request body", "category"],
            )

    if updated_group.name:
        updated_group.name = updated_group.name.lower()

    old_group = await controller.find_group_by_id(id=group_id)

    updated_group_checker_dict = {
        "name": old_group["name"],
        "category": old_group["category"],
        **model_to_dict_without_None(model=updated_group),
    }

    if await controller.group_exists(
        category=updated_group_checker_dict["category"],
        name=updated_group_checker_dict["name"],
    ):
        raise_duplicated_entry_exception(
            message="this item already exists",
            location=["request body", "name"],
        )

    result = await controller.update_group_info(
        id=group_id,
        updated_group=model_to_dict_without_None(model=updated_group),
        updated_by=current_user_id,
    )

    group = await controller.find_group_by_id(id=group_id)

    if not result or not group:
        raise_operation_failed_exception(
            message="problem while updating group"
        )

    return models.SingleGroupResponseModel(
        success=True,
        group=dict_to_model(model=models.GroupReadModel, dict_model=group),
    )


@item_router.post("/", response_model=models.SingleItemResponseModel)
async def create_item(
    new_item: models.ItemBaseModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(new_item.group):
        raise_unprocessable_value_exception(
            message=f"invalid group_id={new_item.group}",
            location=["request body", "group"],
        )

    if not await controller.find_group_by_id(id=new_item.group):
        raise_not_found_exception(
            message=f"no group was found with {new_item.group} id",
            location=["request body", "group"],
        )

    for accompaniment in new_item.accompaniments:
        if not ObjectId.is_valid(accompaniment):
            raise_unprocessable_value_exception(
                message=f"invalid item_id={accompaniment}",
                location=[
                    "request body",
                    "accompaniments",
                    new_item.accompaniments.index(accompaniment),
                ],
            )

        item = await controller.find_item_by_id(id=accompaniment)
        if item:
            if not item.get("is_accompaniment"):
                raise_unprocessable_value_exception(
                    message=f"this item [id={accompaniment}] can't be an accompaniment",
                    location=[
                        "request body",
                        "accompaniments",
                        new_item.accompaniments.index(accompaniment),
                    ],
                )
        else:
            raise_not_found_exception(
                message=f"no menu item[accompaniment] found with id={accompaniment}",
                location=[
                    "request body",
                    "accompaniments",
                    new_item.accompaniments.index(accompaniment),
                ],
            )

    new_item.name = new_item.name.lower()

    if await controller.item_exists(
        name=new_item.name,
        group=new_item.group,
    ):
        raise_duplicated_entry_exception(
            message="this item already exists",
            location=["request body", "name"],
        )

    await controller.create_item(
        new_item=new_item.dict(), create_by=current_user_id
    )

    item = await controller.find_one_item(name=new_item.name)
    if not item:
        raise_operation_failed_exception(
            message="problem while creating menu item"
        )

    return models.SingleItemResponseModel(
        success=True,
        item=dict_to_model(
            model=models.ItemReadModel,
            dict_model=item,
        ),
    )


@item_router.get("/{item_id}", response_model=models.SingleItemResponseModel)
async def get_item(
    item_id: str,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(item_id):
        raise_unprocessable_value_exception(
            message=f"invalid item_id={item_id}",
            location=["path parameter", "item_id"],
        )

    item = await controller.find_item_by_id(id=item_id)

    if not item:
        raise_not_found_exception(
            message=f"no item found with an id={item_id}",
            location=["path parameter", "item_id"],
        )

    return models.SingleItemResponseModel(
        success=True,
        item=dict_to_model(model=models.ItemReadModel, dict_model=item),
    )


@item_router.get("/", response_model=models.MultipleItemsResponseModel)
async def get_items(
    name: str | None = None,
    group: str | None = None,
    limit: int = 0,
    skip: int = 0,
    sort_by: list[str] = Query(
        description="append +[for ascending] or -[for descending] before the name to be sorted with. NOTE: (1) no space between the sign and the name, (2) the arrangement/order of the array maters ..."
    ),
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.VIEW_MENU_ITEMS)
    ),
):
    items = await controller.find_many_items(
        name=name,
        group=group,
        limit=limit,
        skip=skip,
        sort_by=sort_by,
    )

    if not type(items) == list:
        raise_operation_failed_exception(
            message="problem while getting menu item"
        )

    return models.MultipleItemsResponseModel(
        success=True,
        items=[
            dict_to_model(
                model=models.ItemReadModel,
                dict_model=item,
            )
            for item in items
        ],
    )


@item_router.patch(
    "/{item_id}",
    response_model=models.SingleItemResponseModel,
)
async def update_item(
    item_id: str,
    updated_item: models.ItemUpdateModel,
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(item_id):
        raise_unprocessable_value_exception(
            message=f"invalid item_id={item_id}",
            location=["path parameter", "item_id"],
        )
    if updated_item.group:
        if not await controller.find_group_by_id(id=updated_item.group):
            raise_not_found_exception(
                message=f"no group was found with {updated_item.group} id",
                location=["request body", "group"],
            )

    if updated_item.name:
        updated_item.name = updated_item.name.lower()

    if updated_item.name or updated_item.group:
        old_item = await controller.find_item_by_id(id=item_id)

        updated_item_checker_dict = {
            "name": old_item["name"],
            "group": old_item["group"],
            **model_to_dict_without_None(model=updated_item),
        }

        if await controller.item_exists(
            group=updated_item_checker_dict["group"],
            name=updated_item_checker_dict["name"],
        ):
            raise_duplicated_entry_exception(
                message="this item already exists",
                location=["request body", "name"],
            )

    result = await controller.update_item_info(
        id=item_id,
        updated_item=model_to_dict_without_None(model=updated_item),
        updated_by=current_user_id,
    )

    item = await controller.find_item_by_id(id=item_id)

    if not result or not item:
        raise_operation_failed_exception(
            message="problem while updating item"
        )

    return models.SingleItemResponseModel(
        success=True,
        item=dict_to_model(model=models.ItemReadModel, dict_model=item),
    )


@item_router.patch(
    "/add_accompaniments/{item_id}",
    response_model=models.SingleItemResponseModel,
)
async def add_item_accompaniments(
    item_id: str,
    accompaniments: list[str],
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(item_id):
        raise_unprocessable_value_exception(
            message=f"invalid item_id={item_id}",
            location=["path parameter", "item_is"],
        )

    for accompaniment in accompaniments:
        if not ObjectId.is_valid(accompaniment):
            raise_unprocessable_value_exception(
                message=f"invalid item_id={accompaniment}",
                location=[
                    "request body",
                    accompaniments.index(accompaniment),
                ],
            )

        item = await controller.find_item_by_id(id=accompaniment)

        if item:
            if not item.get("is_accompaniment"):
                raise_unprocessable_value_exception(
                    message=f"this item [id={accompaniment}] can't be an accompaniment",
                    location=[
                        "request body",
                        accompaniments.index(accompaniment),
                    ],
                )
        else:
            raise_not_found_exception(
                message=f"no menu item[accompaniment] found with id={accompaniment}",
                location=[
                    "request body",
                    accompaniments.index(accompaniment),
                ],
            )

    result = await controller.add_item_accompaniments(
        id=item_id, accompaniments=accompaniments, updated_by=current_user_id
    )

    item = await controller.find_item_by_id(id=item_id)

    print("*" * 12 + "TESTING" + "*" * 12)
    print(item)
    print(result)

    if not result or not item:
        raise_operation_failed_exception(
            message="problem while updating item"
        )

    return models.SingleItemResponseModel(
        success=True,
        item=dict_to_model(model=models.ItemReadModel, dict_model=item),
    )


@item_router.patch(
    "/remove_accompaniments/{item_id}",
    response_model=models.SingleItemResponseModel,
)
async def remove_item_accompaniments(
    item_id: str,
    accompaniments: list[str],
    current_user_id: AuthJWT = Depends(
        EmployeeRoleChecker(required_role=EmployeeRole.MANAGE_MENU_ITEMS)
    ),
):
    if not ObjectId.is_valid(item_id):
        raise_unprocessable_value_exception(
            message=f"invalid item_id={item_id}",
            location=["path parameter", "item_is"],
        )

    for accompaniment in accompaniments:
        if not ObjectId.is_valid(accompaniment):
            raise_unprocessable_value_exception(
                message=f"invalid item_id={accompaniment}",
                location=[
                    "request body",
                    accompaniments.index(accompaniment),
                ],
            )

        item = await controller.find_item_by_id(id=accompaniment)

        if item:
            if not item.get("is_accompaniment"):
                raise_unprocessable_value_exception(
                    message=f"this item [id={accompaniment}] can't be an accompaniment",
                    location=[
                        "request body",
                        accompaniments.index(accompaniment),
                    ],
                )
        else:
            raise_not_found_exception(
                message=f"no menu item[accompaniment] found with id={accompaniment}",
                location=[
                    "request body",
                    accompaniments.index(accompaniment),
                ],
            )

    result = await controller.remove_item_accompaniments(
        id=item_id, accompaniments=accompaniments, updated_by=current_user_id
    )

    item = await controller.find_item_by_id(id=item_id)

    if not result or not item:
        raise_operation_failed_exception(
            message="problem while updating item"
        )

    return models.SingleItemResponseModel(
        success=True,
        item=dict_to_model(model=models.ItemReadModel, dict_model=item),
    )


menu_router.include_router(category_router, prefix="/category")
menu_router.include_router(group_router, prefix="/group")
menu_router.include_router(item_router, prefix="/item")
