from sqlalchemy import Column, String, Text, Date, JSON, Integer, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from typing import List, Optional
import uuid

Base = declarative_base()

class Day(Base):
    """黄道吉日数据模型"""
    __tablename__ = 'days'
    
    id = Column(String, primary_key=True)  # YYYY-MM-DD 格式
    lunar_date = Column(String, nullable=False)  # 农历日期，如"甲辰年九月初一"
    zodiac_of_day = Column(String, nullable=False)  # 当日生肖
    solar_term = Column(String)  # 节气，可为空
    yi = Column(JSON, nullable=False)  # 宜事项列表
    ji = Column(JSON, nullable=False)  # 忌事项列表
    chong_zodiac = Column(String)  # 冲煞生肖
    notes = Column(Text)  # 简明解释
    
    # 关系
    favorites = relationship("Favorite", back_populates="day")

class Favorite(Base):
    """收藏记录模型"""
    __tablename__ = 'favorites'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  # 用户ID（简化版本可使用设备ID）
    date_id = Column(String, ForeignKey('days.id'), nullable=False)
    purpose = Column(String, nullable=False)  # 用途：marriage/move/opening/travel/contract/groundbreaking
    remind_days_before = Column(JSON, nullable=False)  # 提醒天数列表 [7,3,1]
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    day = relationship("Day", back_populates="favorites")

# 数据库连接配置
DATABASE_URL = "sqlite:///./huangdao_calendar.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()