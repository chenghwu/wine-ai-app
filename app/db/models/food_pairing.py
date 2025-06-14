from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.models import Base

class FoodPairingCategory(Base):
    __tablename__ = "food_pairing_categories"

    id = Column(Integer, primary_key=True, index=True)
    wine_id = Column(Integer, ForeignKey("wine_summaries.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    base_category = Column(String(50), nullable=False, default="Other")

    wine_summary = relationship("WineSummary", back_populates="food_pairing_categories")
    examples = relationship("FoodPairingExample", back_populates="category", cascade="all, delete")

    def to_dict(self):
        return {
            "wine": self.wine_summary.wine,
            "category": self.category,
            "base_category": self.base_category,
            "examples": [example.to_dict() for example in self.examples]
        }

class FoodPairingExample(Base):
    __tablename__ = "food_pairing_examples"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("food_pairing_categories.id", ondelete="CASCADE"), nullable=False)
    food = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)

    category = relationship("FoodPairingCategory", back_populates="examples")

    def to_dict(self):
        return {
            "food": self.food,
            "reason": self.reason
        }