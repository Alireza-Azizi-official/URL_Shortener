from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    visits = relationship(
        "URLVisit", back_populates="urls", cascade="all, delete-orphan"
    )


class URLVisit(Base):
    __tablename__ = "url_visits"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    ip_address = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    url = relationship("URL", back_populates="visits")
