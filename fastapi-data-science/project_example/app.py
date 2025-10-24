from fastapi import FastAPI

from chapter03_project.routers.posts import router as posts_router
from chapter03_project.routers.users import router as users_router

app = FastAPI()

# tags arguments helps you to group endpoints in the interactive documentation for better readability. By doing this, the posts and users endpoints will be clearly separated in the documentation.
app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(users_router, prefix="/users", tags=["users"])