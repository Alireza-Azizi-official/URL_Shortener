from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from .db import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String(2048), nullable=False)
    short_code = Column(String(20), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    visits_count = Column(Integer, nullable=False, server_default=func.cast(0, Integer))
    visit_logs = relationship("VisitLog", back_populates="url", cascade="all, delete")


class VisitLog(Base):
    __tablename__ = "visit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)

    url = relationship("URL", back_populates="visit_logs")
