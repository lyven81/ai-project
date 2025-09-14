"""
黄道吉日 APP - 后端API
标准版MVP，所有用户查询结果一致
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import os
import json
from anthropic import Anthropic
import asyncio

from models import get_db, Day, Favorite
from calendar_data import is_good_day_for_purpose, PURPOSE_MAPPING

# FastAPI应用
app = FastAPI(
    title="黄道吉日 APP API",
    version="1.0.0",
    description="标准版黄道吉日查询和推荐服务"
)

# 静态文件服务
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 初始化AI客户端
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if os.getenv("ANTHROPIC_API_KEY") else None

# ==================== 数据模型 ====================

class DayResponse(BaseModel):
    """日期信息响应模型"""
    id: str
    lunar_date: str
    zodiac_of_day: str
    solar_term: Optional[str]
    yi: List[str]
    ji: List[str]
    chong_zodiac: Optional[str]
    notes: str
    
    model_config = ConfigDict(from_attributes=True)

class RecommendationResponse(BaseModel):
    """吉日推荐响应模型"""
    date: str
    lunar_date: str
    zodiac_of_day: str
    solar_term: Optional[str]
    yi: List[str]
    suitable_reasons: List[str]
    notes: str

class FavoriteRequest(BaseModel):
    """收藏请求模型"""
    user_id: str = Field(..., description="用户ID")
    date_id: str = Field(..., description="日期ID(YYYY-MM-DD)")
    purpose: str = Field(..., description="用途：marriage/move/opening/travel/contract/groundbreaking")
    remind_days_before: List[int] = Field([7, 3, 1], description="提醒天数")

class FavoriteResponse(BaseModel):
    """收藏响应模型"""
    id: str
    user_id: str
    date_id: str
    purpose: str
    remind_days_before: List[int]
    created_at: datetime
    day_info: Optional[DayResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class ReminderRequest(BaseModel):
    """提醒设置请求模型"""
    user_id: str
    favorite_id: str
    remind_days_before: List[int]

class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., description="用户消息")
    conversation_history: Optional[List[Dict[str, str]]] = Field([], description="对话历史")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str
    conversation_id: str
    recommendations: Optional[List[RecommendationResponse]] = None
    day_info: Optional[DayResponse] = None

# ==================== API路由 ====================

@app.get("/")
async def root():
    """返回前端页面"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "黄道吉日 APP API", "docs": "/docs"}

@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "service": "黄道吉日 APP", "version": "1.0.0"}

@app.get("/api/days/today", response_model=DayResponse)
def get_today_info(db: Session = Depends(get_db)):
    """获取今日黄历信息"""
    today = date.today().strftime("%Y-%m-%d")
    return get_day_info(today, db)

@app.get("/api/days/{date_str}", response_model=DayResponse)
def get_day_info(date_str: str, db: Session = Depends(get_db)):
    """获取指定日期的黄历信息"""
    try:
        # 验证日期格式
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    day = db.query(Day).filter(Day.id == date_str).first()
    if not day:
        raise HTTPException(status_code=404, detail="未找到该日期的黄历信息")
    
    return day

@app.get("/api/recommend", response_model=List[RecommendationResponse])
def recommend_good_days(
    purpose: str = Query(..., description="用途：marriage/move/opening/travel/contract/groundbreaking"),
    from_date: str = Query(None, description="开始日期(YYYY-MM-DD)，默认为今天"),
    to_date: str = Query(None, description="结束日期(YYYY-MM-DD)，默认为90天后"),
    limit: int = Query(10, ge=1, le=30, description="返回结果数量限制"),
    db: Session = Depends(get_db)
):
    """推荐适合特定用途的吉日"""
    
    # 验证用途
    if purpose not in PURPOSE_MAPPING:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的用途。支持的用途：{', '.join(PURPOSE_MAPPING.keys())}"
        )
    
    # 设置日期范围
    if not from_date:
        from_date = date.today().strftime("%Y-%m-%d")
    if not to_date:
        to_date = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
    
    # 验证日期格式
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
    
    # 查询日期范围内的数据
    days = db.query(Day).filter(
        Day.id >= from_date,
        Day.id <= to_date
    ).order_by(Day.id).all()
    
    good_days = []
    purpose_items = PURPOSE_MAPPING[purpose]
    
    for day in days:
        day_data = {
            "id": day.id,
            "lunar_date": day.lunar_date,
            "zodiac_of_day": day.zodiac_of_day,
            "solar_term": day.solar_term,
            "yi": day.yi,
            "ji": day.ji,
            "chong_zodiac": day.chong_zodiac,
            "notes": day.notes
        }
        
        if is_good_day_for_purpose(day_data, purpose):
            # 找到匹配的宜事项作为推荐理由
            yi_items = [item.split("（")[0] for item in day.yi]
            suitable_reasons = [item for item in purpose_items if item in yi_items]
            
            recommendation = RecommendationResponse(
                date=day.id,
                lunar_date=day.lunar_date,
                zodiac_of_day=day.zodiac_of_day,
                solar_term=day.solar_term,
                yi=day.yi,
                suitable_reasons=suitable_reasons,
                notes=day.notes
            )
            good_days.append(recommendation)
            
            if len(good_days) >= limit:
                break
    
    return good_days

@app.post("/api/favorites", response_model=FavoriteResponse)
def create_favorite(request: FavoriteRequest, db: Session = Depends(get_db)):
    """创建收藏记录"""
    
    # 验证日期是否存在
    day = db.query(Day).filter(Day.id == request.date_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="指定日期不存在")
    
    # 验证用途
    if request.purpose not in PURPOSE_MAPPING:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的用途。支持的用途：{', '.join(PURPOSE_MAPPING.keys())}"
        )
    
    # 检查是否已经收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == request.user_id,
        Favorite.date_id == request.date_id,
        Favorite.purpose == request.purpose
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该日期和用途已经收藏过了")
    
    # 创建新的收藏记录
    favorite = Favorite(
        user_id=request.user_id,
        date_id=request.date_id,
        purpose=request.purpose,
        remind_days_before=request.remind_days_before
    )
    
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    # 返回包含日期信息的响应
    response = FavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        date_id=favorite.date_id,
        purpose=favorite.purpose,
        remind_days_before=favorite.remind_days_before,
        created_at=favorite.created_at,
        day_info=day
    )
    
    return response

@app.get("/api/favorites", response_model=List[FavoriteResponse])
def get_favorites(
    user_id: str = Query(..., description="用户ID"),
    purpose: Optional[str] = Query(None, description="按用途筛选"),
    db: Session = Depends(get_db)
):
    """获取用户的收藏列表"""
    
    query = db.query(Favorite).filter(Favorite.user_id == user_id)
    
    if purpose:
        if purpose not in PURPOSE_MAPPING:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的用途。支持的用途：{', '.join(PURPOSE_MAPPING.keys())}"
            )
        query = query.filter(Favorite.purpose == purpose)
    
    favorites = query.order_by(Favorite.created_at.desc()).all()
    
    # 为每个收藏添加日期信息
    result = []
    for favorite in favorites:
        day = db.query(Day).filter(Day.id == favorite.date_id).first()
        response = FavoriteResponse(
            id=favorite.id,
            user_id=favorite.user_id,
            date_id=favorite.date_id,
            purpose=favorite.purpose,
            remind_days_before=favorite.remind_days_before,
            created_at=favorite.created_at,
            day_info=day if day else None
        )
        result.append(response)
    
    return result

@app.delete("/api/favorites/{favorite_id}")
def delete_favorite(favorite_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    """删除收藏记录"""
    
    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == user_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "收藏已删除"}

@app.post("/api/reminders/subscribe")
def subscribe_reminder(request: ReminderRequest, db: Session = Depends(get_db)):
    """设置提醒（MVP版本返回确认信息，实际通知功能待实现）"""
    
    # 验证收藏记录是否存在
    favorite = db.query(Favorite).filter(
        Favorite.id == request.favorite_id,
        Favorite.user_id == request.user_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    
    # 更新提醒设置
    favorite.remind_days_before = request.remind_days_before
    db.commit()
    
    return {
        "message": "提醒设置成功",
        "favorite_id": request.favorite_id,
        "remind_days_before": request.remind_days_before,
        "note": "MVP版本暂不支持实际通知推送，后续版本将支持"
    }

@app.get("/api/purposes")
def get_purposes():
    """获取支持的用途列表"""
    purposes = {
        "marriage": "结婚",
        "move": "搬家", 
        "opening": "开业",
        "contract": "签约",
        "travel": "旅行",
        "groundbreaking": "动土"
    }
    
    return {
        "purposes": purposes,
        "mapping": PURPOSE_MAPPING
    }

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """获取统计信息"""

    total_days = db.query(Day).count()
    total_favorites = db.query(Favorite).count()

    # 按用途统计收藏数量
    purpose_stats = {}
    for purpose in PURPOSE_MAPPING.keys():
        count = db.query(Favorite).filter(Favorite.purpose == purpose).count()
        purpose_stats[purpose] = count

    return {
        "total_days": total_days,
        "total_favorites": total_favorites,
        "purpose_stats": purpose_stats,
        "date_range": {
            "earliest": db.query(Day).order_by(Day.id).first().id if total_days > 0 else None,
            "latest": db.query(Day).order_by(Day.id.desc()).first().id if total_days > 0 else None
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """与AI进行对话咨询"""

    if not anthropic_client:
        raise HTTPException(status_code=503, detail="AI服务暂不可用，请联系管理员配置API密钥")

    try:
        # 构建系统提示
        system_prompt = """你是一位专业的中国传统黄历顾问，精通中国传统文化、五行理论、生肖学说和黄道吉日选择。

你的职责是：
1. 帮助用户选择适合的吉日进行重要活动（结婚、搬家、开业、签约、旅行、动土等）
2. 解释中国传统历法的含义和文化背景
3. 基于用户的具体情况给出个性化建议
4. 用温和、专业的语调回答用户问题

回答要求：
- 使用简体中文回答
- 保持文化敬畏和传统尊重
- 给出实用的建议和具体的日期推荐
- 如需要查询具体日期信息，请明确告知用户可以查询的日期格式
- 解释选择某个日期的理由和文化背景

可用的活动类型：
- marriage: 结婚
- move: 搬家
- opening: 开业
- contract: 签约
- travel: 旅行
- groundbreaking: 动土"""

        # 构建对话历史
        messages = []
        for msg in request.conversation_history[-5:]:  # 只保留最近5轮对话
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        messages.append({
            "role": "user",
            "content": request.message
        })

        # 调用Claude API
        response = await asyncio.to_thread(
            lambda: anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=messages
            )
        )

        ai_message = response.content[0].text

        # 分析用户意图，如果涉及具体日期查询或推荐，提供相关数据
        recommendations = None
        day_info = None

        # 检查是否询问今日信息
        if any(keyword in request.message.lower() for keyword in ["今天", "今日", "现在"]):
            try:
                today = date.today().strftime("%Y-%m-%d")
                day = db.query(Day).filter(Day.id == today).first()
                if day:
                    day_info = DayResponse(
                        id=day.id,
                        lunar_date=day.lunar_date,
                        zodiac_of_day=day.zodiac_of_day,
                        solar_term=day.solar_term,
                        yi=day.yi,
                        ji=day.ji,
                        chong_zodiac=day.chong_zodiac,
                        notes=day.notes
                    )
            except:
                pass

        # 检查是否需要推荐吉日
        purpose_keywords = {
            "marriage": ["结婚", "婚礼", "嫁娶", "办婚礼"],
            "move": ["搬家", "迁移", "搬迁", "入宅"],
            "opening": ["开业", "开张", "创业", "开店"],
            "contract": ["签约", "签合同", "签字", "合同"],
            "travel": ["旅行", "出行", "旅游", "出差"],
            "groundbreaking": ["动土", "装修", "建房", "施工"]
        }

        detected_purpose = None
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in request.message for keyword in keywords):
                detected_purpose = purpose
                break

        if detected_purpose:
            try:
                # 获取未来30天的推荐
                from_date = date.today().strftime("%Y-%m-%d")
                to_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")

                days = db.query(Day).filter(
                    Day.id >= from_date,
                    Day.id <= to_date
                ).order_by(Day.id).all()

                good_days = []
                purpose_items = PURPOSE_MAPPING.get(detected_purpose, [])

                for day in days:
                    day_data = {
                        "id": day.id,
                        "lunar_date": day.lunar_date,
                        "zodiac_of_day": day.zodiac_of_day,
                        "solar_term": day.solar_term,
                        "yi": day.yi,
                        "ji": day.ji,
                        "chong_zodiac": day.chong_zodiac,
                        "notes": day.notes
                    }

                    if is_good_day_for_purpose(day_data, detected_purpose):
                        yi_items = [item.split("（")[0] for item in day.yi]
                        suitable_reasons = [item for item in purpose_items if item in yi_items]

                        recommendation = RecommendationResponse(
                            date=day.id,
                            lunar_date=day.lunar_date,
                            zodiac_of_day=day.zodiac_of_day,
                            solar_term=day.solar_term,
                            yi=day.yi,
                            suitable_reasons=suitable_reasons,
                            notes=day.notes
                        )
                        good_days.append(recommendation)

                        if len(good_days) >= 5:  # 限制推荐数量
                            break

                recommendations = good_days
            except:
                pass

        return ChatResponse(
            message=ai_message,
            conversation_id=f"{request.user_id}_{datetime.now().timestamp()}",
            recommendations=recommendations,
            day_info=day_info
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务出错: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)