"""
黄道吉日APP测试套件
包含单元测试和集成测试
"""

import pytest
import json
from datetime import date, timedelta
try:
    from fastapi.testclient import TestClient
except ImportError:
    from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from models import get_db, Base, Day, Favorite
from calendar_data import generate_calendar_data, is_good_day_for_purpose

# 测试数据库设置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 重写数据库依赖
app.dependency_overrides[get_db] = override_get_db

# 创建测试客户端
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """设置测试数据库"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 生成测试数据
    db = TestingSessionLocal()
    try:
        # 生成未来30天的测试数据
        today = date.today()
        calendar_data = generate_calendar_data(today, 30)
        
        for day_data in calendar_data:
            day = Day(**day_data)
            db.merge(day)
        
        db.commit()
        print(f"✅ 测试数据库设置完成，生成了{len(calendar_data)}天的数据")
        
    except Exception as e:
        print(f"❌ 测试数据库设置失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    yield
    
    # 清理
    Base.metadata.drop_all(bind=engine)

class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "黄道吉日 APP"

class TestDayAPI:
    """日期API测试"""
    
    def test_get_today_info(self):
        """测试获取今日信息"""
        response = client.get("/api/days/today")
        assert response.status_code == 200
        data = response.json()
        
        # 验证返回字段
        required_fields = ["id", "lunar_date", "zodiac_of_day", "yi", "ji", "notes"]
        for field in required_fields:
            assert field in data
            assert data[field] is not None
        
        # 验证日期格式
        assert data["id"] == date.today().strftime("%Y-%m-%d")
        assert isinstance(data["yi"], list)
        assert isinstance(data["ji"], list)
        assert len(data["yi"]) > 0
        assert len(data["ji"]) > 0
    
    def test_get_specific_date(self):
        """测试获取特定日期信息"""
        test_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = client.get(f"/api/days/{test_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_date
    
    def test_get_invalid_date(self):
        """测试获取无效日期"""
        response = client.get("/api/days/invalid-date")
        assert response.status_code == 400
        assert "日期格式错误" in response.json()["detail"]
    
    def test_get_nonexistent_date(self):
        """测试获取不存在的日期"""
        future_date = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
        response = client.get(f"/api/days/{future_date}")
        assert response.status_code == 404

class TestRecommendAPI:
    """推荐API测试"""
    
    def test_recommend_marriage(self):
        """测试结婚吉日推荐"""
        response = client.get("/api/recommend?purpose=marriage&limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5
        
        if len(data) > 0:
            item = data[0]
            required_fields = ["date", "lunar_date", "zodiac_of_day", "yi", "suitable_reasons"]
            for field in required_fields:
                assert field in item
                assert item[field] is not None
            
            assert isinstance(item["suitable_reasons"], list)
            assert len(item["suitable_reasons"]) > 0
    
    def test_recommend_invalid_purpose(self):
        """测试无效用途推荐"""
        response = client.get("/api/recommend?purpose=invalid")
        assert response.status_code == 400
        assert "不支持的用途" in response.json()["detail"]
    
    def test_recommend_with_date_range(self):
        """测试指定日期范围的推荐"""
        from_date = date.today().strftime("%Y-%m-%d")
        to_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        response = client.get(f"/api/recommend?purpose=move&from_date={from_date}&to_date={to_date}&limit=3")
        assert response.status_code == 200
        data = response.json()
        
        for item in data:
            item_date = item["date"]
            assert from_date <= item_date <= to_date

class TestFavoriteAPI:
    """收藏API测试"""
    
    def test_create_favorite(self):
        """测试创建收藏"""
        test_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        favorite_data = {
            "user_id": "test_user_1",
            "date_id": test_date,
            "purpose": "marriage",
            "remind_days_before": [7, 3, 1]
        }
        
        response = client.post("/api/favorites", json=favorite_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == "test_user_1"
        assert data["date_id"] == test_date
        assert data["purpose"] == "marriage"
        assert data["remind_days_before"] == [7, 3, 1]
        assert "id" in data
        assert "created_at" in data
        assert "day_info" in data
    
    def test_get_favorites(self):
        """测试获取收藏列表"""
        response = client.get("/api/favorites?user_id=test_user_1")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            required_fields = ["id", "user_id", "date_id", "purpose", "remind_days_before", "created_at"]
            for field in required_fields:
                assert field in item
    
    def test_delete_favorite(self):
        """测试删除收藏"""
        # 首先创建一个收藏
        test_date = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        favorite_data = {
            "user_id": "test_user_2",
            "date_id": test_date,
            "purpose": "travel",
            "remind_days_before": [3, 1]
        }
        
        create_response = client.post("/api/favorites", json=favorite_data)
        favorite_id = create_response.json()["id"]
        
        # 删除收藏
        delete_response = client.delete(f"/api/favorites/{favorite_id}?user_id=test_user_2")
        assert delete_response.status_code == 200
        assert "收藏已删除" in delete_response.json()["message"]
        
        # 验证收藏已被删除
        get_response = client.get("/api/favorites?user_id=test_user_2")
        favorites = get_response.json()
        assert len(favorites) == 0

class TestReminderAPI:
    """提醒API测试"""
    
    def test_subscribe_reminder(self):
        """测试订阅提醒"""
        # 先创建一个收藏
        test_date = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
        favorite_data = {
            "user_id": "test_user_3",
            "date_id": test_date,
            "purpose": "opening",
            "remind_days_before": [7, 3, 1]
        }
        
        create_response = client.post("/api/favorites", json=favorite_data)
        favorite_id = create_response.json()["id"]
        
        # 设置提醒
        reminder_data = {
            "user_id": "test_user_3",
            "favorite_id": favorite_id,
            "remind_days_before": [5, 2]
        }
        
        response = client.post("/api/reminders/subscribe", json=reminder_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "提醒设置成功" in data["message"]
        assert data["favorite_id"] == favorite_id
        assert data["remind_days_before"] == [5, 2]

class TestPurposesAPI:
    """用途API测试"""
    
    def test_get_purposes(self):
        """测试获取用途列表"""
        response = client.get("/api/purposes")
        assert response.status_code == 200
        data = response.json()
        
        assert "purposes" in data
        assert "mapping" in data
        assert isinstance(data["purposes"], dict)
        assert isinstance(data["mapping"], dict)
        
        # 验证包含基本用途
        basic_purposes = ["marriage", "move", "opening", "contract", "travel", "groundbreaking"]
        for purpose in basic_purposes:
            assert purpose in data["purposes"]

class TestStatsAPI:
    """统计API测试"""
    
    def test_get_stats(self):
        """测试获取统计信息"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["total_days", "total_favorites", "purpose_stats", "date_range"]
        for field in required_fields:
            assert field in data
        
        assert data["total_days"] >= 0
        assert data["total_favorites"] >= 0
        assert isinstance(data["purpose_stats"], dict)
        assert isinstance(data["date_range"], dict)

class TestCalendarLogic:
    """黄历逻辑测试"""
    
    def test_generate_calendar_data(self):
        """测试黄历数据生成"""
        test_date = date.today()
        data = generate_calendar_data(test_date, 5)
        
        assert len(data) == 5
        for day_data in data:
            assert "id" in day_data
            assert "lunar_date" in day_data
            assert "zodiac_of_day" in day_data
            assert "yi" in day_data
            assert "ji" in day_data
            assert "notes" in day_data
            
            assert isinstance(day_data["yi"], list)
            assert isinstance(day_data["ji"], list)
            assert len(day_data["yi"]) > 0
            assert len(day_data["ji"]) > 0
    
    def test_is_good_day_for_purpose(self):
        """测试用途匹配逻辑"""
        # 创建测试数据
        day_data = {
            "id": "2025-09-10",
            "yi": ["嫁娶（结婚典礼）", "祭祀（祭拜先祖）", "祈福（祈求福运）"],
            "ji": ["动土（开始建设）", "破土（开始动工）"],
        }
        
        # 测试结婚用途（应该匹配）
        assert is_good_day_for_purpose(day_data, "marriage") == True
        
        # 测试动土用途（应该不匹配，因为在忌项中）
        assert is_good_day_for_purpose(day_data, "groundbreaking") == False

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])