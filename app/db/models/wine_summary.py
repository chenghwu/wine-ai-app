from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.models import Base

class WineSummary(Base):
    __tablename__ = "wine_summaries"

    id = Column(Integer, primary_key=True, index=True)
    wine = Column(String(255), index=True, nullable=False)
    query_text = Column(Text, nullable=False)

    appearance = Column(Text)
    nose = Column(Text)
    palate = Column(Text)
    quality = Column(String(50))
    aging = Column(Text)
    average_price = Column(String(50))
    analysis = Column(Text)
    sat = Column(JSONB, nullable=True)
    reference_source = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "wine": self.wine or "",
            "query_text": self.query_text or "",
            "appearance": self.appearance or "",
            "nose": self.nose or "",
            "palate": self.palate or "",
            "aging": self.aging or "",
            "average_price": self.average_price or "",
            "quality": self.quality or "",
            "analysis": self.analysis or "",
            "sat": self.sat or {},
            "reference_source": self.reference_source or [],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }