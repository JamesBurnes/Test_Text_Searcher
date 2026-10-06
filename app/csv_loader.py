import csv
import ast
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document
from app import elastic, crud
from app.config import settings


async def load_csv_if_empty(session: AsyncSession):
    if await crud.get_count(session) > 0:
        print("DB already has documents, skipping CSV load")
        return

    rows = []
    with open(settings.csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = (row.get("text") or "").strip()
            if not text:
                continue

            raw_rubrics = row.get("rubrics") or ""
            try:
                rubrics = ast.literal_eval(raw_rubrics)
                if not isinstance(rubrics, list):
                    rubrics = [str(rubrics)]
            except (ValueError, SyntaxError):
                cleaned = raw_rubrics.strip("[]").replace("'", "")
                rubrics = [r.strip() for r in cleaned.split(",") if r.strip()]

            try:
                created = datetime.fromisoformat((row.get("created_date") or "").strip())
            except (ValueError, AttributeError):
                continue

            rows.append(Document(rubrics=rubrics, text=text, created_date=created))

    if not rows:
        print("CSV is empty, nothing to load")
        return

    session.add_all(rows)
    await session.commit()

    for r in rows:
        await session.refresh(r)
        await elastic.index_document(r.id, r.text)

    print(f"Loaded {len(rows)} documents")