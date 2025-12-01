"""
Routery dla bloga i stron statycznych.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import get_current_user_optional, get_current_user
from app.models import User, BlogPost, BlogCategory, BlogTag, StaticPage

router = APIRouter()


def slugify(text: str) -> str:
    """Konwertuje tekst na slug (URL-friendly format)."""
    import re
    import unicodedata

    # Normalizacja unicode i konwersja polskich znaków
    text = unicodedata.normalize('NFKD', text)
    # Mapowanie polskich znaków
    polish_chars = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'a', 'Ć': 'c', 'Ę': 'e', 'Ł': 'l', 'Ń': 'n',
        'Ó': 'o', 'Ś': 's', 'Ź': 'z', 'Ż': 'z',
    }
    for pl, en in polish_chars.items():
        text = text.replace(pl, en)

    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text[:100]


# ============== PUBLICZNE STRONY ==============

async def get_menu_pages(db: AsyncSession) -> List[StaticPage]:
    """Pobiera strony do menu."""
    result = await db.execute(
        select(StaticPage)
        .where(StaticPage.is_in_menu == True)
        .order_by(StaticPage.menu_order)
    )
    return result.scalars().all()


@router.get("/blog", response_class=HTMLResponse, name="blog_list")
async def blog_list(
    request: Request,
    page: int = 1,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Lista wpisów bloga (publiczna)."""
    from app.main import templates

    per_page = 10
    offset = (page - 1) * per_page

    # Bazowe zapytanie
    query = select(BlogPost).where(BlogPost.is_published == True)

    # Filtrowanie po kategorii
    if category:
        query = query.join(BlogCategory).where(BlogCategory.slug == category)

    # Filtrowanie po tagu
    if tag:
        query = query.join(BlogPost.tags).where(BlogTag.slug == tag)

    # Pobierz wpisy z relacjami
    query = (
        query
        .options(selectinload(BlogPost.category), selectinload(BlogPost.tags), selectinload(BlogPost.author))
        .order_by(BlogPost.published_at.desc())
        .offset(offset)
        .limit(per_page)
    )

    result = await db.execute(query)
    posts = result.scalars().all()

    # Liczba wszystkich wpisów (dla paginacji)
    count_query = select(func.count(BlogPost.id)).where(BlogPost.is_published == True)
    if category:
        count_query = count_query.join(BlogCategory).where(BlogCategory.slug == category)
    if tag:
        count_query = count_query.join(BlogPost.tags).where(BlogTag.slug == tag)

    total_result = await db.execute(count_query)
    total_posts = total_result.scalar()
    total_pages = (total_posts + per_page - 1) // per_page

    # Pobierz kategorie i tagi dla sidebara
    categories_result = await db.execute(select(BlogCategory).order_by(BlogCategory.name))
    categories = categories_result.scalars().all()

    tags_result = await db.execute(select(BlogTag).order_by(BlogTag.name))
    tags = tags_result.scalars().all()

    menu_pages = await get_menu_pages(db)

    return templates.TemplateResponse(
        "blog/list.html",
        {
            "request": request,
            "user": user,
            "posts": posts,
            "categories": categories,
            "tags": tags,
            "current_category": category,
            "current_tag": tag,
            "page": page,
            "total_pages": total_pages,
            "menu_pages": menu_pages,
        },
    )


@router.get("/blog/{slug}", response_class=HTMLResponse, name="blog_post")
async def blog_post(
    request: Request,
    slug: str,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Pojedynczy wpis bloga (publiczny)."""
    from app.main import templates

    result = await db.execute(
        select(BlogPost)
        .options(selectinload(BlogPost.category), selectinload(BlogPost.tags), selectinload(BlogPost.author))
        .where(BlogPost.slug == slug)
        .where(BlogPost.is_published == True)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")

    menu_pages = await get_menu_pages(db)

    return templates.TemplateResponse(
        "blog/post.html",
        {
            "request": request,
            "user": user,
            "post": post,
            "menu_pages": menu_pages,
        },
    )


@router.get("/strona/{slug}", response_class=HTMLResponse, name="static_page")
async def static_page(
    request: Request,
    slug: str,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Strona statyczna (publiczna)."""
    from app.main import templates

    result = await db.execute(
        select(StaticPage).where(StaticPage.slug == slug)
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Strona nie znaleziona")

    menu_pages = await get_menu_pages(db)

    return templates.TemplateResponse(
        "static_page.html",
        {
            "request": request,
            "user": user,
            "page": page,
            "menu_pages": menu_pages,
        },
    )


# ============== PANEL ADMINA ==============

def require_admin(user: User = Depends(get_current_user)) -> User:
    """Wymaga uprawnień administratora."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Brak uprawnień administratora")
    return user


@router.get("/admin", response_class=HTMLResponse, name="admin_dashboard")
async def admin_dashboard(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Panel administracyjny - dashboard."""
    from app.main import templates

    # Statystyki
    posts_count = await db.execute(select(func.count(BlogPost.id)))
    pages_count = await db.execute(select(func.count(StaticPage.id)))
    categories_count = await db.execute(select(func.count(BlogCategory.id)))

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": {
                "posts": posts_count.scalar(),
                "pages": pages_count.scalar(),
                "categories": categories_count.scalar(),
            },
        },
    )


# ----- Wpisy bloga -----

@router.get("/admin/posts", response_class=HTMLResponse, name="admin_posts")
async def admin_posts(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lista wpisów bloga w panelu admina."""
    from app.main import templates

    result = await db.execute(
        select(BlogPost)
        .options(selectinload(BlogPost.category))
        .order_by(BlogPost.created_at.desc())
    )
    posts = result.scalars().all()

    return templates.TemplateResponse(
        "admin/posts_list.html",
        {"request": request, "user": user, "posts": posts},
    )


@router.get("/admin/posts/new", response_class=HTMLResponse, name="admin_post_new")
async def admin_post_new(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Formularz nowego wpisu."""
    from app.main import templates

    categories = await db.execute(select(BlogCategory).order_by(BlogCategory.name))
    tags = await db.execute(select(BlogTag).order_by(BlogTag.name))

    return templates.TemplateResponse(
        "admin/post_form.html",
        {
            "request": request,
            "user": user,
            "post": None,
            "categories": categories.scalars().all(),
            "tags": tags.scalars().all(),
        },
    )


@router.post("/admin/posts/new", response_class=HTMLResponse, name="admin_post_create")
async def admin_post_create(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(None),
    category_id: Optional[int] = Form(None),
    tags_str: str = Form(""),
    is_published: bool = Form(False),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Tworzenie nowego wpisu."""
    slug = slugify(title)

    # Sprawdź unikalność sluga
    existing = await db.execute(select(BlogPost).where(BlogPost.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    post = BlogPost(
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt if excerpt else None,
        category_id=category_id if category_id else None,
        author_id=user.id,
        is_published=is_published,
        published_at=datetime.now() if is_published else None,
    )

    # Obsługa tagów
    if tags_str:
        tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
        for tag_name in tag_names:
            tag_slug = slugify(tag_name)
            result = await db.execute(select(BlogTag).where(BlogTag.slug == tag_slug))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = BlogTag(name=tag_name, slug=tag_slug)
                db.add(tag)
                await db.flush()
            post.tags.append(tag)

    db.add(post)
    await db.commit()

    return RedirectResponse(url="/admin/posts", status_code=302)


@router.get("/admin/posts/{post_id}/edit", response_class=HTMLResponse, name="admin_post_edit")
async def admin_post_edit(
    request: Request,
    post_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Formularz edycji wpisu."""
    from app.main import templates

    result = await db.execute(
        select(BlogPost)
        .options(selectinload(BlogPost.tags))
        .where(BlogPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")

    categories = await db.execute(select(BlogCategory).order_by(BlogCategory.name))
    tags = await db.execute(select(BlogTag).order_by(BlogTag.name))

    return templates.TemplateResponse(
        "admin/post_form.html",
        {
            "request": request,
            "user": user,
            "post": post,
            "categories": categories.scalars().all(),
            "tags": tags.scalars().all(),
        },
    )


@router.post("/admin/posts/{post_id}/edit", response_class=HTMLResponse)
async def admin_post_update(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str = Form(None),
    category_id: Optional[int] = Form(None),
    tags_str: str = Form(""),
    is_published: bool = Form(False),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Aktualizacja wpisu."""
    result = await db.execute(
        select(BlogPost)
        .options(selectinload(BlogPost.tags))
        .where(BlogPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Wpis nie znaleziony")

    post.title = title
    post.content = content
    post.excerpt = excerpt if excerpt else None
    post.category_id = category_id if category_id else None

    # Obsługa publikacji
    if is_published and not post.is_published:
        post.published_at = datetime.now()
    post.is_published = is_published

    # Aktualizuj tagi
    post.tags.clear()
    if tags_str:
        tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
        for tag_name in tag_names:
            tag_slug = slugify(tag_name)
            result = await db.execute(select(BlogTag).where(BlogTag.slug == tag_slug))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = BlogTag(name=tag_name, slug=tag_slug)
                db.add(tag)
                await db.flush()
            post.tags.append(tag)

    await db.commit()

    return RedirectResponse(url="/admin/posts", status_code=302)


@router.post("/admin/posts/{post_id}/delete")
async def admin_post_delete(
    post_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Usuwanie wpisu."""
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()

    if post:
        await db.delete(post)
        await db.commit()

    return RedirectResponse(url="/admin/posts", status_code=302)


# ----- Kategorie -----

@router.get("/admin/categories", response_class=HTMLResponse, name="admin_categories")
async def admin_categories(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lista kategorii."""
    from app.main import templates

    result = await db.execute(select(BlogCategory).order_by(BlogCategory.name))
    categories = result.scalars().all()

    return templates.TemplateResponse(
        "admin/categories_list.html",
        {"request": request, "user": user, "categories": categories},
    )


@router.post("/admin/categories/new")
async def admin_category_create(
    name: str = Form(...),
    description: str = Form(None),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Tworzenie nowej kategorii."""
    slug = slugify(name)

    existing = await db.execute(select(BlogCategory).where(BlogCategory.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Kategoria o takiej nazwie już istnieje")

    category = BlogCategory(name=name, slug=slug, description=description)
    db.add(category)
    await db.commit()

    return RedirectResponse(url="/admin/categories", status_code=302)


@router.post("/admin/categories/{category_id}/delete")
async def admin_category_delete(
    category_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Usuwanie kategorii."""
    result = await db.execute(select(BlogCategory).where(BlogCategory.id == category_id))
    category = result.scalar_one_or_none()

    if category:
        await db.delete(category)
        await db.commit()

    return RedirectResponse(url="/admin/categories", status_code=302)


# ----- Strony statyczne -----

@router.get("/admin/pages", response_class=HTMLResponse, name="admin_pages")
async def admin_pages(
    request: Request,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Lista stron statycznych."""
    from app.main import templates

    result = await db.execute(select(StaticPage).order_by(StaticPage.menu_order))
    pages = result.scalars().all()

    return templates.TemplateResponse(
        "admin/pages_list.html",
        {"request": request, "user": user, "pages": pages},
    )


@router.get("/admin/pages/new", response_class=HTMLResponse, name="admin_page_new")
async def admin_page_new(
    request: Request,
    user: User = Depends(require_admin),
):
    """Formularz nowej strony."""
    from app.main import templates

    return templates.TemplateResponse(
        "admin/page_form.html",
        {"request": request, "user": user, "page": None},
    )


@router.post("/admin/pages/new")
async def admin_page_create(
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    is_in_menu: bool = Form(False),
    menu_order: int = Form(0),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Tworzenie nowej strony."""
    slug_clean = slugify(slug)

    existing = await db.execute(select(StaticPage).where(StaticPage.slug == slug_clean))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Strona o takim adresie URL już istnieje")

    page = StaticPage(
        title=title,
        slug=slug_clean,
        content=content,
        is_in_menu=is_in_menu,
        menu_order=menu_order,
    )
    db.add(page)
    await db.commit()

    return RedirectResponse(url="/admin/pages", status_code=302)


@router.get("/admin/pages/{page_id}/edit", response_class=HTMLResponse, name="admin_page_edit")
async def admin_page_edit(
    request: Request,
    page_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Formularz edycji strony."""
    from app.main import templates

    result = await db.execute(select(StaticPage).where(StaticPage.id == page_id))
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Strona nie znaleziona")

    return templates.TemplateResponse(
        "admin/page_form.html",
        {"request": request, "user": user, "page": page},
    )


@router.post("/admin/pages/{page_id}/edit")
async def admin_page_update(
    page_id: int,
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    is_in_menu: bool = Form(False),
    menu_order: int = Form(0),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Aktualizacja strony."""
    result = await db.execute(select(StaticPage).where(StaticPage.id == page_id))
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Strona nie znaleziona")

    slug_clean = slugify(slug)

    # Sprawdź unikalność sluga (dla innych stron)
    existing = await db.execute(
        select(StaticPage)
        .where(StaticPage.slug == slug_clean)
        .where(StaticPage.id != page_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Strona o takim adresie URL już istnieje")

    page.title = title
    page.slug = slug_clean
    page.content = content
    page.is_in_menu = is_in_menu
    page.menu_order = menu_order

    await db.commit()

    return RedirectResponse(url="/admin/pages", status_code=302)


@router.post("/admin/pages/{page_id}/delete")
async def admin_page_delete(
    page_id: int,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Usuwanie strony."""
    result = await db.execute(select(StaticPage).where(StaticPage.id == page_id))
    page = result.scalar_one_or_none()

    if page:
        await db.delete(page)
        await db.commit()

    return RedirectResponse(url="/admin/pages", status_code=302)


# ----- Upload obrazów -----

@router.post("/admin/upload-image")
async def admin_upload_image(
    file: UploadFile = File(...),
    user: User = Depends(require_admin),
):
    """Upload obrazu do wpisów bloga."""
    import uuid
    from pathlib import Path
    from app.config import settings

    # Sprawdź typ pliku
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Dozwolone są tylko obrazy (JPG, PNG, GIF, WebP)")

    # Utwórz katalog na obrazy
    images_dir = Path("./data/uploads/images")
    images_dir.mkdir(parents=True, exist_ok=True)

    # Generuj unikalną nazwę
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = images_dir / unique_name

    # Zapisz plik
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # max 5MB
        raise HTTPException(status_code=400, detail="Obraz jest zbyt duży (max 5 MB)")

    with open(file_path, "wb") as f:
        f.write(content)

    # Zwróć URL do obrazu
    return {"url": f"/uploads/images/{unique_name}"}
