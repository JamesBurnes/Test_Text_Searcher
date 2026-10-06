from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)