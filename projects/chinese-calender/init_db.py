"""
数据库初始化脚本
生成黄道吉日种子数据并填充数据库
"""

from models import create_tables, SessionLocal, Day
from calendar_data import generate_calendar_data
from datetime import date
import json

def init_database():
    """初始化数据库并填充种子数据"""
    print("正在创建数据库表...")
    create_tables()
    
    print("正在生成黄道吉日数据...")
    # 生成从今天开始的90天数据
    today = date.today()
    calendar_data = generate_calendar_data(today, 90)
    
    # 保存数据到数据库
    db = SessionLocal()
    try:
        print("正在填充数据到数据库...")
        for day_data in calendar_data:
            day = Day(**day_data)
            db.merge(day)  # 使用merge避免重复插入
        
        db.commit()
        print(f"成功填充{len(calendar_data)}天的数据到数据库")
        
    except Exception as e:
        print(f"数据库填充错误: {e}")
        db.rollback()
    finally:
        db.close()
    
    # 同时保存为JSON文件作为备份
    with open("calendar_seed_data.json", "w", encoding="utf-8") as f:
        json.dump(calendar_data, f, ensure_ascii=False, indent=2)
    print("种子数据已保存为 calendar_seed_data.json")

def show_sample_data():
    """显示部分样本数据"""
    db = SessionLocal()
    try:
        sample_days = db.query(Day).limit(3).all()
        
        print("\n=== 样本数据 ===")
        for day in sample_days:
            print(f"\n日期: {day.id}")
            print(f"农历: {day.lunar_date}")
            print(f"生肖: {day.zodiac_of_day}")
            print(f"节气: {day.solar_term or '无'}")
            print(f"冲煞: 冲{day.chong_zodiac}")
            print(f"宜: {', '.join(day.yi[:3])}...")
            print(f"忌: {', '.join(day.ji[:3])}...")
            print(f"说明: {day.notes}")
            print("-" * 50)
            
    except Exception as e:
        print(f"查询样本数据错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    show_sample_data()