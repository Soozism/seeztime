"""
Translation model for internationalization support
"""

from sqlalchemy import Column, Integer, String, Text, Index

from app.core.database import Base

class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(50), nullable=False)
    model_id = Column(Integer, nullable=False)
    field_name = Column(String(50), nullable=False)
    language = Column(String(10), nullable=False)
    value = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Translation {self.model_type}.{self.field_name} ({self.language})>"


# Add indexes for better performance
Index("idx_translation_model_type_id", Translation.model_type, Translation.model_id)
Index("idx_translation_language", Translation.language)
