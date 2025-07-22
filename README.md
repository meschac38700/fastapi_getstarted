[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fr.eliam-lotonga.fastapi-getstarted&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=fr.eliam-lotonga.fastapi-getstarted)

#### FastAPI template project

> [!NOTE]
> This web application serves as a starter kit for building robust APIs using
> the FastAPI framework. It provides a foundational structure that includes
> built-in authentication, a permission management system, and other useful features.
> The goal is to offer developers a streamlined starting point,
> simplifying the initial setup and promoting a better development experience.

#### Python Version:

###### *_python >= 3.13.X_*

[K8s repo](https://github.com/meschac38700/k8s_fastapi_getstarted)

# Get started

Rename the folder **envs.example** to **envs** Then change the environment
information

# Build Application environment

### Install dependencies
##### required at least:
###### *_uv == 0.5.29_*

---

We use
[uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) to
manage dependencies: The following command will install all project dependencies in a
virtual environment.

By default, uv will create a virtual env in a hidden folder named `.venv` if you want to
change the location and name, you can set
[UV_PROJECT_ENVIRONMENT](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path)
as environment variable before running the following command.

```console
$ uv sync --all-extras
```

Next we need to activate the virtual environment created by uv previously

```console
$ source ./.venv/bin/activate
```

#### Setup `direnv`

> [!NOTE]
> This is optional but recommended to automatically export the environment variables
> needed to run the local server.
>
> direnv is an extension for your shell. It augments existing shells with a new feature
> that can load and unload environment variables depending on the current directory.

Get started with [direnv](https://direnv.net/#getting-started) Once direnv is installed
all you have to do is to allow the `.envrc` file

```console
$ cd getstarted
$ direnv allow .
```

if you don't want to configure `direnv`, you need to export `APP_ENVIRONMENT` every time
you move to the project directory:

```console
$ export APP_ENVIRONMENT=dev
```

## Run the application

##### Run prod server

```console
$ docker compose up
```

##### Run development server

```console
$ python src/manage.py server
```

##### Using docker compose
```console
$ docker compose -f docker-compose.dev.yaml up -d
```

#### Run application tests
```console
$ python src/manage.py tests
```

<a id="run_migrations"></a>
#### Running migrations

We use [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) to manage
migrations. The following commands, as explained in the documentation, will allow you to
create and run the migrations.

```console
$ cd src
$ alembic revision --autogenerate -m "message of commit"
$ alembic upgrade head
```
#### Load fixtures
```console
$ python src/manage.py fixtures
```
---
## Understand the structure of the application

- [Apps package](#apps)
- [Models](#models)
  - [Schemas](#schemas)
  - [Migrations](#migrations)
- [Routers](#routers)
- [Fixtures](#fixtures)
- [Signals](#signals)

If you are familiar with the Django application structure, you will find almost the same approach in this project.

<a id="apps"></a>
### Apps package
This folder is generally where you will be working most of the time and where all your work will reside.
you can think of it as a Django project in which you can create all the applications you need.

It contains all the project's existing applications.
To add a new application, simply create a new package in this folder.
For example, let's say we want to add an application that will manage our blog posts.
The following tree illustrates what our blog post application might look like.
A valid application package requires at least a models and routers modules.

<details markdown="1">
<summary>App complete tree</summary>

```
apps/
└── blog
    ├── __init__.py
    ├── commands
    │   ├── __init__.py
    │   └── latest_posts.py
    ├── dependencies
    │   ├── __init__.py
    │   └── access_rights.py
    ├── fixtures
    │   ├── initial_posts.yaml
    │   └── test
    │       └── fake_posts.yaml
    ├── models
    │   ├── __init__.py
    │   ├── schemas
    │   │   ├── __init__.py
    │   │   ├── create.py
    │   │   └── patch.py
    │   └── post.py
    ├── routers
    │   ├── __init__.py
    │   └── posts.py
    ├── signals
    │   ├── __init__.py
    │   ├── after_create_post.py
    │   └── before_create_post.py
    ├── tasks
    │   ├── __init__.py
    │   └── load_initial_posts.py
    ├── templates
    │   └── blog
    │       └── list_posts.html
    ├── tests
    │   ├── tasks
    │   │   ├── __init__.py
    │   │   └── test_load_initial_posts.py
    │   ├── __init__.py
    │   ├── test_signals.py
    │   └── test_post_crud_operations.py
    └── utils
        ├── __init__.py
        └── types.py
```
</details>

## Now let's take a closer look at the `Apps package`.

---
<a id="models"></a>
### Models package
This could be a simple module or a package in which you could
define all models related to your application.

#### Example:

<details markdown="1">
<summary>File: apps.post.models.py</summary>

```Python
from sqlmodel import Field

from core.db.models import SQLTable
from core.db.mixins import BaseTable


# This base model will be useful later for declaring Pydantic schemas.
# For example, we'll use it to declare the following schemas: CreatePost or UpdatePost
class PostBaseModel(SQLTable):
    title: str
    description: str | None

# This is our final model (ORM)
# Extends BaseTable to define some generic fields, such as: id, created_at, updated_at
class Post(PostBaseModel, BaseTable, table=True):
    pass
```
</details>

**You can use the package approach if you have many models to define.**

<details markdown="1">
<summary>Here's what the folder structure looks like:</summary>

```
apps/
└── blog
    └── models
        ├── __init__.py
        ├── statistical.py
        └── post.py
```
###### File: apps.post.models.post.py
```Python
from sqlmodel import Field, Relationship

from apps.user.models import User
from core.db.models import SQLTable
from core.db.mixins import BaseTable



# This base model will be useful later for declaring Pydantic schemas.
# For example, we'll use it to declare the following schemas: CreatePost or UpdatePost
class PostBaseModel(SQLTable):
    title: str
    description: str | None

# This is our final model (ORM)
class Post(PostBaseModel, BaseTable, table=True):
    author_username: str | None = Field(
        default=None, foreign_key="users.username", ondelete="SET NULL"
    )
    author: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
```
###### File: apps.post.models.statistical.py
```Python
from sqlmodel import Relationship, Field

from .post import Post
from core.db.models import SQLTable
from core.db.mixins import BaseTable


class PostStatisticalBaseModel(SQLTable):
    view_number: int = Field(default=0)
    shared_number: int = Field(default=0)

class PostStatistical(PostStatisticalBaseModel, BaseTable, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
    post_id: int = Field(default=None, foreign_key="post.id", ondelete="CASCADE")
    post: Post = Relationship(sa_relationship_kwargs={"lazy": "joined"})
```

> [!IMPORTANT]
> Since this is a package, we need to explicitly export these models in the __init__ file

###### File: apps.post.models.__init__.py

```Python
from .post import PostBaseModel, Post
from .statistical import PostStatisticalBaseModel, PostStatistical

__all__ = [
    "Post",
    "PostBaseModel",
    "PostStatistical",
    "PostStatisticalBaseModel",
]
```
</details>

<a id="migrations"></a>
#### All that remains is to create migrations and run them.
[Perform migrations](#run_migrations)

---
<a id="schemas"></a>
### Schemas module
The schemas are Pydantic models based on our SQLModel tables.
We need them to validate user data. So let's create some Post schemas:

<details markdown="1">
<summary>File: apps.post.models.schemas.post.py</summary>

```Python
from apps.post.models.post import PostBaseModel

class PostUpdate(PostBaseModel):
    """Validate user data with an http PUT/PATCH request to update a post."""

    class ConfigDict:
        from_attributes = True


class PostCreate(PostBaseModel):
    """Validate user data with an http POST request to create a post."""

    class ConfigDict:
        from_attributes = True
```
</details>

> [!IMPORTANT]
> And similarly, since we chose the package approach,
> we need to explicitly export these schemas

<details markdown="1">
<summary>File: apps.post.models.schemas.__init__.py</summary>

```Python
from .post import PostCreate, PostUpdate

__all__ = [
    "PostCreate",
    "PostUpdate",
]
```
</details>

<details markdown="1">
<summary>Here's what the folder structure looks like:</summary>

```
apps/
└── blog
    └──models
       ├── __init__.py
       ├── post.py
       ├── statistical.py
       └── schemas
           ├── __init__.py
           └── post.py
```
</details>

---
<a id="routers"></a>
### Routers package
This package, like the "models" package, can be a package or a module.
This is where you'll define all the endpoints related to your application.

Let's implement an example based on our previous `Post` and `PostStatistical` models.

<details markdown="1">
<summary>File: apps.post.routers.post.py</summary>

```Python
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from apps.post.models import Post
from apps.post.models.schema import PostCreate, PostUpdate


routers = APIRouter(prefix="/posts")

# GET /blog/posts/
@routers.get("/")
async def posts():
    return await Post.all()

@routers.post("/")
async def create_post(post: PostCreate):
    return await Post(**post.model_dump()).save()

@routers.get("/{pk}/")
async def get_post(pk: int):
    post = await Post.get(id=pk)
    if post is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Post {pk} not found.")
    return post

@routers.put("/{pk}/")
async def update_post(pk: int, post: PostUpdate):
    stored_post = await Post.get(id=pk)
    if stored_post is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Post {pk} not found.")
    return await Post(**post.model_dump()).save()

@routers.delete("/{pk}/")
async def delete_post(pk: int):
    stored_post = await Post.get(id=pk)
    if stored_post is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Post {pk} not found.")
    return await stored_post.delete()
```
</details>

<details markdown="1">
<summary>apps.post.routers.statistical.py:</summary>

```Python
from fastapi import APIRouter

from apps.post.models import PostStatistical

routers = APIRouter(prefix="/{post_id}/statisticals")

# GET /blog/posts/{post_id}/statiticals/
@routers.get("/")
async def post_statisticals(post_id: int):
    return await PostStatistical.filter(post_id=post_id)
```
</details>

<details markdown="1">
<summary>apps.post.routers.__init__.py:</summary>

```Python
from fastapi import APIRouter

from .post import routers as post_routers
from .statistical import routers as statistical_routers

routers = APIRouter(tags=["Blog"], prefix="/blog")
routers.include_router(post_routers)
routers.include_router(statistical_routers)

__all__ = ["routers"]
```
</details>


<details markdown="1">
<summary>This is what our blog app looks like so far, with everything we've added:</summary>

```
apps/
└── blog
    ├── models
    │   ├── __init__.py
    │   ├── post.py
    │   ├── statistical.py
    │   └── schemas
    │   │   ├── __init__.py
    │   │   └── post.py
    └──  routers
         ├── __init__.py
         ├── post.py
         └── statistical.py
```
</details>

> [!IMPORTANT]
> At this point, your blog application is fully functional.
> You can run the development server to check it.

---
<a id="permissions"></a>
### Authorization (Permissions/Groups)
#### Why Permissions?
It's a common thought: why bother with a complex permission system when a simple "Depends" seems to do the trick?</br>
While both might appear similar at first glance, they are actually complementary, not contradictory.</br>
You can certainly define a router using "Depends" for access control, and the reverse is also true.</br>
However, it's crucial to see permissions as a more advanced and dynamic control system.</br>
</br>
##### Let's Look at Concrete Examples:</br>
If you've ever used social media apps like Twitch, Facebook, or WhatsApp, you've probably encountered features such as:
  - <b>Blocking a friend</b> or limiting online visibility to specific friends (Facebook)
  - <b>Blocking a viewer in chat</b> (Twitch)
  - <b>Limiting who can see your status</b> or profile picture (WhatsApp)

All these features rely on a permission system behind the scenes.</br>
Where "Depends" is configured once and remains static, permissions allow us to make user action control dynamic,</br>
even after the application is deployed.</br>

###### Consider the Twitch example again:
The chat is available to any viewer, as long as they are logged into the platform.</br>
However, the streamer can block this access if a viewer spams or misbehaves.</br>
We can imagine that Twitch has a permission system in place to enable this action.</br>
Through their settings, a streamer can add or remove a permission for a viewer.</br>
(Of course, it's not presented this way to the streamer, who simply sees "Block" or "Unblock," but a similar process is happening in the background.)</br>
</br>
This is the core benefit of permissions.</br>
They provide the flexibility and control needed for real-time, adaptable access management in complex applications.
</br>
</br>

Now that we understand the difference between `Depends` and `Permissions`,
Let's see how to implement them in our `Blog` application.


##### Implementing `Depends` for authentication and Ownership
`Depends` is perfect for reusable, programmatic checks that are part of the request flow.

<details markdown="1">
<summary>blog.dependencies.access.py:</summary>

```Python
from fastapi import Depends, HTTPException, status

from apps.blog.models import Post
from apps.authentication.dependencies.oauth2 import current_user


async def get_post_if_owner(pk: int, user: Depends(current_user)):
    """Dependency to get a post and ensure the current user is its owner."""
    post = await Post.get(id=pk)
    if post is None:
        detail = f"Post {pk} not found."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if post.author_id != user.id:
        detail = "Not authorized to access this post"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    return post
```

Then use it in certain Post routers
```Python
# blog.routers.post.py
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from apps.blog.dependencies.access import get_post_if_owner
from apps.post.models.schema import PostCreate, PostUpdate
from apps.blog.models import Post

routers = APIRouter(prefix="/posts")

@routers.get("/{pk}/")
async def get_post(post: Annotated[Post, Depends(get_post_if_owner)]):
    return post

@routers.put("/{pk}/")
async def update_post(post: Annotated[Post, Depends(get_post_if_owner)], post_data: PostUpdate):
    post.update_from_dict(post_data.model_dump(exclude_unset=True))
    return await post.save()

@routers.delete("/{pk}/")
async def delete_post(post: Annotated[Post, Depends(get_post_if_owner)]):
    return await post.delete()
```
</details>

##### Implementing `Permissions` for dynamic control
Permissions, in contrast to `Depends`, involve <b>dynamic checks based on data stored in the database</b>(or a dedicated permission service).</br>

Let's imagine we want to restrict viewing post statitics to certain users or an "admin".</br>

We can add a `can_view_stats` permission to users or `group`.

You can either use fixtures (recommended) or manually create the permission.

There's a command to install fixtures listed in the `INITIAL_FIXTURES` variable within your `settings/constants.py` file.

Once you've created your fixture file (`blog.fixtures.blog_initial_permissions.yaml`), <br>
add its file name to this variable and run the following command:</br>

```Python
class AppConstants:
    ...
    INITIAL_FIXTURES = [
      ...,
      "blog_initial_permissions",
    ]
    ...
```

```console
python src/manage.py fixtures
```

<details markdown="1">
<summary>The fixture could look like this:</summary>

```YAML
- model: authorization.Permission
  properties:
    name: can_view_stats
    target_table: poststatistical
```
</details>

For the manual approach (not recommended):

```console
$ cd src
$ python
Python 3.13.0 (main, Oct 16 2024, 03:23:02) [Clang 18.1.8 ] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import asyncio
>>> from apps.user.models import User
>>> from apps.authorization.models import Group, Permission
>>> can_view_stats = asyncio.run(Permission.get(name="can_view_stats"))
>>> user = asyncio.run(User.first())
>>> group = asyncio.run(Group.first())
>>> asyncio.run(user.add_permission(can_view_stats))
>>> asyncio.run(group.add_permission(can_view_stats))
```

<details markdown="1">
<summary>The python module approach could look like this:</summary>

```python
# file foo.py
import asyncio
from apps.user.models import User
from apps.authorization.models import Group, Permission


async def get_user_and_group():
    return await asyncio.gather(
        User.first(),
        Group.first()
    )

async def apply_view_stats_permission(user: User, group: Group):
    """Apply the 'can_view_stats' permission to a user and a group."""
    can_view_stats = await Permission.get(name="can_view_stats").save()
    await user.add_permission(can_view_stats)
    # And to the group
    await group.add_permission(can_view_stats)


if __name__ == "__main__":
    user, group = get_user_and_group()
    asyncio.run(apply_view_stats_permission(user, group))
```

</details>

Let's see how to use that permission in your application:
<details markdown="1">
<summary>apps.blog.routers.statistical.py</summary>

> [!NOTE]
> You can apply permissions either to the user or to a group.
> In this example, we check either option.
> If the user or their group has the permission, or if the user is an admin,
> then they are authorized to view the Post's stats.

```Python
from fastapi import APIRouter, Depends

from apps.post.models import PostStatistical
from apps.authorization.dependencies import permission_required

routers = APIRouter(prefix="/{post_id}/statisticals")

# GET /blog/posts/{post_id}/statiticals/
@routers.get("/",
    dependencies=[
        Depends(
            permission_required(permissions=["can_view_stats"], groups=["can_view_stats"])
        )
    ]
)
async def post_statisticals(post_id: int):
    return await PostStatistical.filter(post_id=post_id)

```

> [!NOTE]
> As you can also see, the other advantage of permissions here is
> that we don't have to write any extra lines of code; simply adding the permission
> to the database is all it takes, and the decorator at the router level.

</details>


<details markdown="1">
<summary>This is what our blog app looks like so far, with everything we've added:</summary>

```
apps/
└── blog
    ├── dependencies
    │   ├── __init__.py
    │   └── access.py
    ├── fixtures
    │   └── blog_initial_permissions.yaml
    ├── models
    │   ├── __init__.py
    │   ├── post.py
    │   ├── statistical.py
    │   └── schemas
    │   │   ├── __init__.py
    │   │   └── post.py
    └──  routers
         ├── __init__.py
         ├── post.py
         └── statistical.py
```
</details>

---
<a id="fixtures"></a>
### Fixtures package
Now that we've added some endpoints, we need to test our application.
We could take a TDD approach, but it depends on you and which approach you're most effective with.

This is the perfect transition to introduce the `fixtures` package.

Fixtures are YAML files in which we define data for testing purposes. They can also be called "fake data."

All you need is to create your fixture YAML file then define in your Test class a `fixtures` variable,
which contains the name of your fixture file.

Enough blah blah, let's put this into practice.

<details markdown="1">
<summary>apps.blog.fixtures.testing.posts.yaml</summary>

###### apps.blog.fixtures.testing.posts.yaml
```YAML
- model: user.User
  properties:
    username: d.john
    first_name: John
    last_name: DOE
    password: john_pass
    email: john.doe@example.org
    role: staff

- model: user.User
  properties:
    username: d.jane
    first_name: Jane
    last_name: DOE
    password: jane_pass
    email: jane@example.org
    role: active

---

- model: blog.Post
  properties:
    author_username: d.john
    title: X Chief Says She Is Leaving the Social Media Platform
    description: >
      Linda Yaccarino, whom Elon Musk hired to run X in 2023, grappled
      with the challenges the company faced after Mr. Musk took over. 13h agoBy
      Mike Isaac and Kate Conger Linda Yaccarino at a Senate Judiciary Committee
      hearing in 2024. She grew close to Elon Musk in 2023 when, as an executive
      at NBCUniversal, she pledged to keep running ads on Twitter as other
      advertisers were refusing to do so.
      CreditKenny Holston/The New York Times

- model: blog.Post
  properties:
    author_username: d.jane
    title: OpenAI and Microsoft Bankroll New A.I. Training for Teachers
    description: >
      The American Federation of Teachers said it would use the $23 million, including $500,000 from the A.I.
      start-up Anthropic, to create a national training center.
      By Natasha SINGER
```
</details>

Now that our fixtures file is ready, let's implement the tests

Since our blog application is a dedicated folder, it is a good practice to have all associated logic in this folder.
We will create the tests folder inside the blog folder

<details markdown="1">
<summary>apps.blog.tests.test_post_crud_operations.py</summary>

```Python
from fastapi import status

from core.unittest.async_case import AsyncTestCase
from apps.blog.models import Post


# AsyncTestCase is a wrapper class of IsolatedAsyncioTestCase
# It includes some logics to manage fixtures, client and so on
class TestPostCrudOperations(AsyncTestCase):
    fixtures = [
      "posts" # declaration of our fixtures (extension .yaml is optional)
    ]

    async def test_get_all_posts(self):
        response = await self.client.get("/blog/posts/")

        posts = response.json()

        assert status.HTTP_200_OK == response.status_code
        assert len(posts) >= 2

    async def test_get_post_not_found(self):
        post_id = -1
        response = await self.client.get(f"/blog/posts/{post_id}")
        expected = {
          "detail": f"Post {post_id} not found."
        }
        assert expected == response.json()

    async def test_get_post(self):
        post_id = 1
        response = await self.client.get(f"/blog/posts/{post_id}")
        expected = await Post.get(id=post_id)
        assert expected.model_dump(mode="json") == response.json()

    # And so on
```
</details>

<details markdown="1">
<summary>Here's what the folder structure looks like:</summary>

```
apps/
└── blog
    ├── dependencies
    │   ├── __init__.py
    │   └── access.py
    ├── fixtures
    │   ├── blog_initial_permissions.yaml
    │   └── testing
    │       └── posts.yaml
    ├── models
    │   ├── __init__.py
    │   ├── post.py
    │   ├── statistical.py
    │   └── schemas
    │       ├── __init__.py
    │       └── post.py
    ├── routers
    │     ├── __init__.py
    │     ├── post.py
    │     └── statistical.py
    └── tests
        └── test_post_crud_operations.py
```
</details>

---
<a id="signals"></a>
### Signals package
Signals allow us to intervene before or after an action in our SQL table.
There is a signal handling class that will help you easily add signals to your model.
Let's implement an example signal with the Post model.

```Python
# TODO(Eliam): Work in progress
```

<details markdown="1">
<summary>Here's what the folder structure looks like:</summary>

```
apps/
└── blog
    ├── dependencies
    │   ├── __init__.py
    │   └── access.py
    ├── fixtures
    │   ├── blog_initial_permissions.yaml
    │   └── testing
    │       └── posts.yaml
    ├── models
    │   ├── __init__.py
    │   ├── post.py
    │   ├── statistical.py
    │   └── schemas
    │       ├── __init__.py
    │       └── post.py
    ├── routers
    │   ├── __init__.py
    │   ├── post.py
    │   └── statistical.py
    ├── signals
    │   ├── __init__.py
    │   ├── after_create.py
    │   └── before_create.py
    └── tests
        ├── test_signals.py
        └── test_post_crud_operations.py
```
</details>
