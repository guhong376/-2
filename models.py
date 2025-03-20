from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    address = Column(String(200))
    house_type = Column(String(50))
    area = Column(Float)
    direction = Column(String(50))
    follow_info = Column(String(100))
    total_price = Column(Float)
    unit_price = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    # 添加索引
    __table_args__ = (
        Index('idx_area_price', 'area', 'total_price'),
        Index('idx_direction', 'direction'),
        Index('idx_house_type', 'house_type'),
        Index('idx_created_at', 'created_at')
    )

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 