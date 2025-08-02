from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from apps.authorization.models import Group
from apps.authorization.models.schema.group import GroupCreate, GroupUpdate
from apps.authorization.models.schema.permission import PermissionList
from apps.user.dependencies.roles import AdminAccess
from apps.user.models.schema.create import UserList

routers = APIRouter()

_NOT_FOUND_MSG = "Group not found."


@routers.get(
    "/",
    name="group-list",
    description="Get all groups",
    dependencies=[Depends(AdminAccess())],
)
async def get_groups(
    name: str | None = None,
    target_table: str | None = None,
    offset: int = 0,
    limit: int = 100,
):
    filters = {}
    if name is not None:
        filters["name__startswith"] = name

    if target_table is not None:
        filters["target_table"] = target_table

    return await (
        Group.filter(**filters, offset=offset, limit=limit) if filters else Group.all()
    )


@routers.post(
    "/",
    name="group-create",
    description="Create a new group",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.CREATED,
)
async def create_group(group_data: GroupCreate):
    return await Group(**group_data.model_dump()).save()


@routers.patch(
    "/{pk}/",
    name="group-patch",
    description="Patch a group",
    dependencies=[Depends(AdminAccess())],
)
async def patch_group(pk: int, group_data: GroupUpdate):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    if group_data.check_all_fields_updated(group.model_dump()):
        detail = "Cannot use PATCH to update entire registry, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    group.update_from_dict(group_data.model_dump(exclude_unset=True))

    return await group.save()


@routers.put(
    "/{pk}/",
    name="group-update",
    description="Update a group",
    dependencies=[Depends(AdminAccess())],
)
async def put_group(pk: int, group_data: GroupCreate):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)
    # if all required fields are not updated, pydantic error will be generated (GroupCreate)
    group_data.check_all_required_fields_updated(group.model_dump())

    group.update_from_dict(group_data.model_dump(exclude_unset=True))

    return await group.save()


@routers.delete(
    "/{pk}/",
    name="group-delete",
    description="Delete a group",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_group(pk: int):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    await group.delete()


@routers.patch(
    "/{pk}/users/add/",
    name="group-add-user",
    description="Add some users to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def add_users_to_group(pk: int, users: UserList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    await group.extend_users(await users.to_object_list())

    return group.users


@routers.patch(
    "/{pk}/users/remove/",
    name="group-remove-user",
    description="Remove some user to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def remove_users_to_group(pk: int, users: UserList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    await group.remove_users(await users.to_object_list())

    return group.users


@routers.patch(
    "/{pk}/permissions/add/",
    name="group-add-permissions",
    description="Add some permissions to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def add_permissions_to_group(pk: int, permissions: PermissionList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    await group.extend_permissions(await permissions.to_object_list())

    return group.get_permissions()


@routers.patch(
    "/{pk}/permissions/remove/",
    name="group-remove-permissions",
    description="Remove some permissions to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def remove_permissions_to_group(pk: int, permissions: PermissionList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    await group.remove_permissions(await permissions.to_object_list())

    return group.get_permissions()
