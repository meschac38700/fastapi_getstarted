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

```bash
uv sync --all-extras
```

Next we need to activate the virtual environment created by uv previously

```bash
source ./.venv/bin/activate
```

#### Setup `direnv`

> [!NOTE]
>
> This is optional but recommended to automatically export the environment variables
> needed to run the local server.
>
> direnv is an extension for your shell. It augments existing shells with a new feature
> that can load and unload environment variables depending on the current directory.

Get started with [direnv](https://direnv.net/#getting-started) Once direnv is installed
all you have to do is to allow the `.envrc` file

```bash
cd getstarted
direnv allow .
```

if you don't want to configure `direnv`, you need to export `APP_ENVIRONMENT` every time
you move to the project directory:

```bash
export APP_ENVIRONMENT=dev
```

## Run the application

##### Run prod server

```bash
docker compose up
```

##### Run development server

```bash
python manage.py server
```

##### Using docker compose
```bash
docker compose -f docker-compose.dev.yaml up -d
```

#### Run application tests
```bash
python manage.py tests
```

#### Running migrations

We use [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) to manage
migrations. The following commands, as explained in the documentation, will allow you to
create and run the migrations.

```bash
cd src
alembic revision --autogenerate -m "message of commit"
alembic upgrade head
```
#### Load fixtures
```bash
python manage.py fixtures
```
---
### Explanation of the application structure

If you are familiar with the Django application structure, you will find almost the same approach in this project.

#### `Apps` folder
This folder is generally where you will be working most of the time and where all your work will reside.
you can think of it as a Django project in which you can create all the applications you need.

It contains all the project's existing applications.
To add a new application, simply create a new package in this folder.
For example, let's say we want to add an application that will manage our blog posts.
The following tree illustrates what our blog post application might look like.
A valid application package requires at least a models and routers modules.
```
apps/
└── blog
    ├── __init__.py
    ├── dependencies
    │   ├── __init__.py
    │   └── access_rights.py
    ├── fixtures
    │   ├── initial_posts.yaml
    │   └── test
    │       └── fake_posts.yaml
    ├── models
    │   ├── __init__.py
    │   ├── schema
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

#### Now let's take a closer look at the `App folder`.

##### `Models` package
This could be a simple module or a package in which you could
define all models related to your application.

Example:
```Python
# apps.post.models.py
from sqlmodel import Field

from core.db.models import SQLTable
from core.db.mixins import TimestampedModelMixin


# This base model will be useful later for declaring Pydantic schemas.
# For example, we'll use it to declare the following schemas: CreatePost or UpdatePost
class PostBaseModel(TimestampedModelMixin, SQLTable):
    title: str
    description: str | None

# This is our final model (ORM)
class Post(PostBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
```
**You can use the package approach if you have many models to define.**

Here's what it looks like:
```
apps/
└── blog
    └── models
        ├── __init__.py
        ├── statistical.py
        └── post.py
```
```Python
# apps.post.models.__init__.py
from .post import Post
from .statistical import PostStatistical

__all__ = [
    "Post",
    "PostStatistical",
]
```
```Python
# apps.post.models.post.py
from typing import Optional
from sqlmodel import Field, Relationship

from core.db.models import SQLTable
from core.db.mixins import TimestampedModelMixin


# This base model will be useful later for declaring Pydantic schemas.
# For example, we'll use it to declare the following schemas: CreatePost or UpdatePost
class PostBaseModel(TimestampedModelMixin, SQLTable):
    title: str
    description: str | None

# This is our final model (ORM)
class Post(PostBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
    statistical: Optional["PostStatistical"] =  Relationship(back_populates="post")
```

```Python
# apps.post.models.statistical.py
from sqlmodel import Relationship, Field

from .post import Post
from core.db.models import SQLTable
from core.db.mixins import TimestampedModelMixin


class PostStatisticalBaseModel(TimestampedModelMixin, SQLTable):
    view_number: int = Field(default=0)
    shared_number: int = Field(default=0)

class PostStatistical(PostStatisticalBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
    post_id: int = Field(default=None, foreign_key="post.id")
    post: Post = Relationship(back_populates="statistical", sa_relationship_kwargs={"lazy": "joined"})
```

##### `routers` package
Now let's talk about the "routers" package.
This package, like the "models" package, can be a package or a module.
This is where you'll define all the endpoints related to your application.

Let's implement an example based on our previous `Post` and `PostStatistical` models.

Here's what it looks like:
```
apps/
└── blog
    ├── models
    │   ├── __init__.py
    │   ├── post.py
    │   └── statistical.py
    └──  routers
        ├── __init__.py
        ├── post.py
        └── statistical.py
```

First, we will create schemas so that we can use them to validate user data.
###### Schema module
```Python
# apps.post.models.schema.py
from apps.post.models.post import PostBaseModel

class PostUpdate(PostBaseModel):
    class ConfigDict:
        from_attributes = True

class PostCreate(PostBaseModel):
    class ConfigDict:
        from_attributes = True
```
#### Now let's focus on routers

```Python
# apps.post.routers.post.py
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


```Python
# apps.post.routers.statistical.py
from fastapi import APIRouter

from apps.post.models import PostStatistical

routers = APIRouter(prefix="/{post_id}/statisticals")

# GET /blog/posts/{post_id}/statiticals/
@routers.get("/")
async def post_statisticals(post_id: int):
    return await PostStatistical.filter(post_id=post_id)
```

```Python
# apps.post.routers.__init__.py
from fastapi import APIRouter

from .post import routers as post_routers
from .statistical import routers as statistical_routers

routers = APIRouter(tags=["Blog"], prefix="/blog")
routers.include_router(post_routers)
routers.include_router(statistical_routers)

__all__ = ["routers"]
```
> [!IMPORTANT]
> It is important that this exported variable is named as `routers`
