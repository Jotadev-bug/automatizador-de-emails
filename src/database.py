import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

class EmailLog(Base):
    __tablename__ = 'email_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    sender = Column(String, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=True) # Opcional por ahora
    action_taken = Column(String, nullable=False)

    __table_args__ = (
        Index('idx_timestamp', timestamp),
        Index('idx_predicted_class', predicted_class)
    )

def init_db():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'logs.db')
    
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()
