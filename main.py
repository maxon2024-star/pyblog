from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, select, Field
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from faker import Faker
from passlib.context import CryptContext  # Для работы с хешированием паролей
# Импорт моделей, метаданных и engine в конец файла
from sqlmodel import SQLModel

# Экспорт для Alembic
Base = SQLModel

# Обработчик для старта и завершения работы приложения
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Запуск приложения...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    print("Завершение работы приложения...")

# Создаем приложение FastAPI с использованием lifespan
app = FastAPI(lifespan=lifespan)

# Подключение к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:05062012@localhost:5432/pyblog"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Настройка bcrypt для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from sqlmodel import Field, Relationship, SQLModel
from typing import List

# Модель Post
class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str
    user_id: int = Field(default=None, foreign_key="user.id")  # Внешний ключ для связи с User

    # Связь с пользователем
    user: "User" = Relationship(back_populates="posts")

# Модель User
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str  # Будет хранить хеш пароля

    # Связь с постами
    posts: List[Post] = Relationship(back_populates="user")


# Функция для получения сессии
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


from fastapi import Cookie, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Функция для проверки существующего пользователя
async def get_current_user(
    session: AsyncSession = Depends(get_session),
    username: str = Cookie(default=None),
):
    if not username:  # Если cookie отсутствует
        return None

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    return user


# Шаблоны и статические файлы
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    page: int = 1,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),  # Добавлено
):
    POSTS_PER_PAGE = 10
    offset = (page - 1) * POSTS_PER_PAGE

    # Получаем посты с учетом пагинации
    result = await session.execute(select(Post).offset(offset).limit(POSTS_PER_PAGE))
    posts = result.scalars().all()

    # Подсчитываем общее количество постов
    total_posts_result = await session.execute(select(Post))
    total_posts = len(total_posts_result.scalars().all())
    total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "posts": posts,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,  # Передаем пользователя в шаблон
        },
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    hashed_password = pwd_context.hash(password)  # Хешируем пароль
    new_user = User(username=username, password=hashed_password)
    session.add(new_user)
    await session.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

from fastapi.responses import Response

@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    # Проверяем наличие пользователя
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Неверный логин или пароль. Попробуйте снова.", "username": username},
            status_code=401,
        )

    # Устанавливаем cookie для авторизации
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="username", value=user.username, httponly=True)
    return response

#где логин, там и разлогин
@app.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(key="username")
    return response


from sqlalchemy import func  # Импорт функции для подсчёта записей

@app.get("/posts", response_class=HTMLResponse)
async def get_posts(
    request: Request,
    page: int = 1,
    session: AsyncSession = Depends(get_session),
):
    POSTS_PER_PAGE = 10
    offset = (page - 1) * POSTS_PER_PAGE

    # Подсчёт общего количества записей
    result = await session.execute(select(func.count(Post.id)))
    total_posts = result.scalar_one()

    # Логика для расчёта страниц
    total_pages = (total_posts + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    if page < 1 or page > total_pages:
        raise HTTPException(status_code=404, detail="Страница не найдена")

    # Получение постов для текущей страницы
    result = await session.execute(
        select(Post).offset(offset).limit(POSTS_PER_PAGE)
    )
    posts = result.scalars().all()

    # Лог для отладки
    print(f"Текущая страница: {page}, Всего страниц: {total_pages}")
    print(f"Посты на странице: {len(posts)}")
    for post in posts:
        print(f"Post ID: {post.id}, Title: {post.title}")

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "posts": posts,
            "current_page": page,
            "total_pages": total_pages,
        },
    )


@app.get("/posts/create", response_class=HTMLResponse)
async def create_post_page(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})


from fastapi import Depends, HTTPException
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

@app.post("/posts/create")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),  # Получаем текущего пользователя
):
    if not user:  # Проверяем, залогинен ли пользователь
        raise HTTPException(status_code=401, detail="Вы должны быть авторизованы для создания поста")

    if not title or not content:  # Проверяем заполненность данных
        raise HTTPException(status_code=400, detail="Заголовок и содержимое обязательны")

    # Создание нового поста
    new_post = Post(title=title, content=content, user_id=user.id)
    session.add(new_post)

    try:
        await session.commit()  # Асинхронный commit
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении поста: {str(e)}")

    return RedirectResponse("/", status_code=303)


# Генерация случайных пользователей и постов
faker = Faker()

@app.get("  ")
async def generate_data(session: AsyncSession = Depends(get_session)):
    for _ in range(5):  # Создаем 5 пользователей
        hashed_password = pwd_context.hash(faker.password())
        user = User(username=faker.user_name(), password=hashed_password)
        session.add(user)

    for _ in range(20):  # Создаем 20 постов
        post = Post(title=faker.sentence(), content=faker.paragraph())
        session.add(post)

    await session.commit()
    return {"message": "Данные успешно сгенерированы"}
