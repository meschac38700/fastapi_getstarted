from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from apps.authorization.models.group import Group
from apps.authorization.models.pydantic.group import GroupCreate, GroupUpdate
from apps.authorization.models.pydantic.permission import PermissionList
from apps.user.dependencies.roles import AdminAccess
from apps.user.models.pydantic.create import UserList

routers = APIRouter()


@routers.get("/", name="List all groups", dependencies=[Depends(AdminAccess())])
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
    name="Create new Group",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.CREATED,
)
async def create_group(group_data: GroupCreate):
    return await Group(**group_data.model_dump()).save()


@routers.patch(
    "/{pk}/",
    name="Patch a Group",
    dependencies=[Depends(AdminAccess())],
)
async def patch_group(pk: int, group_data: GroupUpdate):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")

    if group_data.check_all_fields_updated(group.model_dump()):
        detail = "Cannot use PATCH to update entire registry, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    if not group_data.is_updated:
        return group

    group.update_from_dict(group_data.model_dump(exclude_unset=True))

    return await group.save()


@routers.put(
    "/{pk}/",
    name="Update a Group",
    dependencies=[Depends(AdminAccess())],
)
async def put_group(pk: int, group_data: GroupCreate):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")
    # if all required fields are not updated, pydantic error will be generated (GroupCreate)
    group_data.check_all_required_fields_updated(group.model_dump())
    if not group_data.is_updated:
        return group

    group.update_from_dict(group_data.model_dump(exclude_unset=True))

    return await group.save()


@routers.delete(
    "/{pk}/",
    name="Delete a Group",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_group(pk: int):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")

    await group.delete()


@routers.post(
    "/{pk}/users/add/",
    name="Add some users to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def add_users_to_group(pk: int, users: UserList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")

    await group.extend_users(await users.to_object_list())

    return group.users


@routers.post(
    "/{pk}/users/remove/",
    name="Remove some user to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def remove_users_to_group(pk: int, users: UserList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")

    await group.remove_users(await users.to_object_list())

    return group.users


@routers.post(
    "/{pk}/permissions/add/",
    name="Add some permissions to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def add_permissions_to_group(pk: int, permissions: PermissionList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")

    await group.extend_permissions(await permissions.to_object_list())

    return group.get_permissions()


@routers.post(
    "/{pk}/permissions/remove/",
    name="Remove some permissions to a certain group",
    dependencies=[Depends(AdminAccess())],
)
async def remove_permissions_to_group(pk: int, permissions: PermissionList):
    group = await Group.get(id=pk)
    if group is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Group not found.")

    await group.remove_permissions(await permissions.to_object_list())

    return group.get_permissions()
