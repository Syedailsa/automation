import asyncio
import uuid

from app.database import async_session_factory, init_db
from app.models.user import User
from app.models.notebook import Notebook
from app.models.source import Source


async def seed():
    await init_db()
    async with async_session_factory() as db:
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            name="Test User",
            google_id="1234567890",
            preferred_llm="openai",
        )
        db.add(user)
        await db.flush()

        notebook = Notebook(
            id=uuid.uuid4(),
            user_id=user.id,
            title="My First Notebook",
            description="A test notebook for development",
            status="active",
        )
        db.add(notebook)
        await db.flush()

        source = Source(
            id=uuid.uuid4(),
            notebook_id=notebook.id,
            title="Sample URL Source",
            source_type="url",
            url="https://example.com/article",
            status="ready",
        )
        db.add(source)

        await db.commit()
        print(f"Seeded user: {user.email} (ID: {user.id})")
        print(f"Seeded notebook: {notebook.title} (ID: {notebook.id})")
        print(f"Seeded source: {source.title} (ID: {source.id})")


if __name__ == "__main__":
    asyncio.run(seed())
