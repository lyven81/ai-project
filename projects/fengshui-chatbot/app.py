import os
import random
import math
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date
from enum import Enum

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from anthropic import Anthropic, APIStatusError

# 設定 Anthropic API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic_client: Optional[Anthropic] = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# FastAPI 應用程式
app = FastAPI(
    title="專業風水顧問",
    version="2.0.0",
    description="基於傳統風水學原理的智慧風水顧問，提供居家環境與運勢改善建議"
)

# 設定模板
templates = Jinja2Templates(directory=".")

# =========================
# 風水學知識庫系統
# =========================

class FengshuiElement(Enum):
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"

class BaguaArea(Enum):
    CAREER = "事業(坎)"
    KNOWLEDGE = "知識(艮)"
    FAMILY = "家庭(震)"
    WEALTH = "財富(巽)"
    FAME = "名聲(離)"
    LOVE = "愛情(坤)"
    CHILDREN = "子女(兌)"
    HELPFUL = "貴人(乾)"
    CENTER = "中心(太極)"

class QuestionCategory(Enum):
    LOVE = "感情"
    CAREER = "事業"
    HEALTH = "健康"
    GENERAL = "綜合"
    FINANCE = "財運"
    HOME = "居家環境"

# 詳細風水元素資料庫
FENGSHUI_ELEMENTS_DATABASE = {
    "木": {
        "english": "Wood",
        "season": "春季",
        "direction": "東方",
        "colors": ["綠色", "藍綠色", "深藍色"],
        "keywords": ["成長", "生機", "創新", "發展", "上進"],
        "strengths": ["創意豐富", "適應力強", "成長中", "積極進取"],
        "challenges": ["缺乏耐心", "易受外界影響", "過於理想化"],
        "supporting_element": "水",
        "controlling_element": "金",
        "numbers": [3, 4],
        "bagua_areas": ["家庭(震)", "財富(巽)"]
    },
    "火": {
        "english": "Fire",
        "season": "夏季",
        "direction": "南方",
        "colors": ["紅色", "橙色", "紫色"],
        "keywords": ["熱情", "能量", "光明", "活躍", "變化"],
        "strengths": ["充滿活力", "熱情洋溢", "具有魅力", "光芒四射"],
        "challenges": ["易燥躁不安", "易衝動行事", "需要平衡"],
        "supporting_element": "木",
        "controlling_element": "水",
        "numbers": [2, 7],
        "bagua_areas": ["名聲(離)"]
    },
    "土": {
        "english": "Earth",
        "season": "長夏",
        "direction": "中央",
        "colors": ["黃色", "棕色", "米色"],
        "keywords": ["穩定", "包容", "滋養", "平衡", "中和"],
        "strengths": ["穩重踏實", "包容性強", "具有凝聚力", "平衡協調"],
        "challenges": ["過於保守", "變化緩慢", "易固步自封"],
        "supporting_element": "火",
        "controlling_element": "木",
        "numbers": [5, 10],
        "bagua_areas": ["中心(太極)"]
    },
    "金": {
        "english": "Metal",
        "season": "秋季",
        "direction": "西方",
        "colors": ["白色", "金色", "銀色"],
        "keywords": ["收斂", "肅殺", "正義", "剛毅", "純潔"],
        "strengths": ["意志堅強", "講求正義", "行事果斷", "追求完美"],
        "challenges": ["過於嚴厲", "缺乏彈性", "易生肅殺之氣"],
        "supporting_element": "土",
        "controlling_element": "火",
        "numbers": [6, 9],
        "bagua_areas": ["貴人(乾)", "子女(兌)"]
    },
    "水": {
        "english": "Water",
        "season": "冬季", 
        "direction": "北方",
        "colors": ["黑色", "深藍色", "藏青色"],
        "keywords": ["流動", "智慧", "靈動", "包容", "深度"],
        "strengths": ["具有智慧", "適應力強", "包容性大", "洞察力深"],
        "challenges": ["易流於消極", "缺乏恆心", "過度包容"],
        "supporting_element": "金",
        "controlling_element": "土",
        "numbers": [1, 8],
        "bagua_areas": ["事業(坎)"]
    }
}

# 風水元素對應（加入別名支持）
FENGSHUI_ELEMENTS = {
    "木": "木", "木元素": "木", "木行": "木",
    "火": "火", "火元素": "火", "火行": "火", 
    "土": "土", "土元素": "土", "土行": "土",
    "金": "金", "金元素": "金", "金行": "金", "金屬": "金",
    "水": "水", "水元素": "水", "水行": "水"
}

# 八卦方位資料庫
BAGUA_DATABASE = {
    "坎": {"direction": "北方", "element": "水", "area": "事業", "color": "黑色", "season": "冬季"},
    "艮": {"direction": "東北", "element": "土", "area": "知識", "color": "黃色", "season": "冬春之間"},
    "震": {"direction": "東方", "element": "木", "area": "家庭", "color": "綠色", "season": "春季"},
    "巽": {"direction": "東南", "element": "木", "area": "財富", "color": "綠色", "season": "春夏之間"},
    "離": {"direction": "南方", "element": "火", "area": "名聲", "color": "紅色", "season": "夏季"},
    "坤": {"direction": "西南", "element": "土", "area": "愛情", "color": "黃色", "season": "夏秋之間"},
    "兌": {"direction": "西方", "element": "金", "area": "子女", "color": "白色", "season": "秋季"},
    "乾": {"direction": "西北", "element": "金", "area": "貴人", "color": "白色", "season": "秋冬之間"}
}

# =========================
# 風水能量計算
# =========================

def get_daily_element(today: date = None) -> Tuple[str, str, str]:
    """根據日期計算當日五行元素"""
    if today is None:
        today = date.today()
    
    # 根據天干地支計算五行（簡化版）
    elements = ["金", "水", "木", "木", "土", "土", "火", "火", "金", "金"]
    day_of_year = today.timetuple().tm_yday
    element = elements[day_of_year % 10]
    
    # 元素能量說明
    element_energy = {
        "金": "收斂及決斷力強，適合整理和計劃",
        "水": "智慧及靈感提升，適合思考和溝通",
        "木": "成長及創新能量，適合新計劃及學習",
        "火": "熱情及表現力強，適合展示及社交",
        "土": "穩定及包容性強，適合建立關係及維護"
    }.get(element, "能量平衡")
    
    return element, element_energy, FENGSHUI_ELEMENTS_DATABASE[element]["direction"]

def calculate_birth_elements(birth_date: str) -> Dict[str, str]:
    """根據出生日期計算個人五行八字（簡化版）"""
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except:
        return {"primary": "木", "secondary": "水", "explanation": "無法解析出生日期，使用預設五行"}
    
    # 天干五行對照（簡化計算）
    heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    stem_elements = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]
    
    # 地支五行對照
    earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    branch_elements = ["水", "土", "木", "木", "土", "火", "火", "土", "金", "金", "土", "水"]
    
    # 年柱計算（簡化版）
    year_stem = (birth.year - 1984) % 10  # 以1984甲子年為基準
    year_branch = (birth.year - 1984) % 12
    
    # 月柱計算（簡化版）
    month_stem = (year_stem * 2 + birth.month) % 10
    month_branch = (birth.month - 1) % 12
    
    # 日柱計算（簡化版）
    days_from_base = (birth - date(1984, 2, 2)).days  # 甲子日為基準
    day_stem = days_from_base % 10
    day_branch = days_from_base % 12
    
    # 主要五行（日干）
    primary_element = stem_elements[day_stem]
    
    # 次要五行（年干或月干）
    secondary_element = stem_elements[year_stem]
    
    # 季節調整
    season_adjustment = {
        (3, 4, 5): "木",    # 春
        (6, 7, 8): "火",    # 夏  
        (9, 10, 11): "金",  # 秋
        (12, 1, 2): "水"    # 冬
    }
    
    for months, element in season_adjustment.items():
        if birth.month in months:
            # 如果出生季節與主五行相同，增強該元素
            if primary_element == element:
                secondary_element = element
            break
    
    explanation = f"根據您的出生日期{birth_date}，推算您的主要五行為{primary_element}，輔助五行為{secondary_element}"
    
    return {
        "primary": primary_element,
        "secondary": secondary_element,
        "explanation": explanation,
        "year_stem": heavenly_stems[year_stem],
        "year_branch": earthly_branches[year_branch],
        "day_stem": heavenly_stems[day_stem],
        "day_branch": earthly_branches[day_branch]
    }

def get_seasonal_energy(today: date = None) -> str:
    """獲取季節能量"""
    if today is None:
        today = date.today()
    
    month = today.month
    if month in [3, 4, 5]:
        return "春季能量旺盛，適合新計劃和成長"
    elif month in [6, 7, 8]:
        return "夏季活力充沛，適合展現和表達"
    elif month in [9, 10, 11]:
        return "秋季收穫時節，適合總結和準備"
    else:
        return "冬季內省時期，適合規劃和蓄力"

def calculate_element_harmony(element1: str, element2: str) -> int:
    """計算五行元素和諧度分數"""
    if element1 not in FENGSHUI_ELEMENTS_DATABASE or element2 not in FENGSHUI_ELEMENTS_DATABASE:
        return 50
    
    data1 = FENGSHUI_ELEMENTS_DATABASE[element1]
    data2 = FENGSHUI_ELEMENTS_DATABASE[element2]
    
    score = 50
    
    # 相生關係（互相生助）
    if data1["supporting_element"] == element2 or data2["supporting_element"] == element1:
        score += 30
    
    # 相同元素（和諧共振）
    if element1 == element2:
        score += 20
    
    # 相剋關係（需要平衡）
    if data1["controlling_element"] == element2 or data2["controlling_element"] == element1:
        score -= 20
    
    # 季節協調性
    seasons1 = [data1["season"]]
    seasons2 = [data2["season"]]
    if any(s in seasons2 for s in seasons1):
        score += 10
    
    return min(95, max(15, score))

# =========================
# 增強的資料模型
# =========================

class ChatIn(BaseModel):
    user: str = Field(..., description="用戶姓名")
    element: Optional[str] = Field(None, description="主要五行元素（木、火、土、金、水）- 可選，未填寫將根據出生日期計算")
    question: str = Field(..., description="想要諮詢的問題")
    category: Optional[QuestionCategory] = Field(None, description="問題類型")
    birth_date: Optional[str] = Field(None, description="出生日期 YYYY-MM-DD（用於計算五行八字，建議填寫）")
    timeframe: Optional[str] = Field("今天", description="時間範圍：今天、本週、本月")
    mood: Optional[str] = Field(None, description="當前心情或能量狀態")
    partner_element: Optional[str] = Field(None, description="伴侶五行元素（感情問題時）")
    home_direction: Optional[str] = Field(None, description="居家朝向或關心的方位")
    birth_time: Optional[str] = Field(None, description="出生時間 HH:MM（可選，用於更精確的八字計算）")

class FengshuiInsight(BaseModel):
    daily_element_influence: str
    seasonal_energy: str
    element_guidance: str
    bagua_guidance: str
    element_harmony_note: Optional[str] = None

class ChatOut(BaseModel):
    title: str
    reply: str
    fengshui_reasoning: str
    tips: List[str]
    timing_advice: str
    affirmation: str
    lucky_elements: Dict[str, Any]
    fengshui_insight: FengshuiInsight
    timeframe: str
    harmony_score: Optional[int] = None

# =========================
# 專業風水學系統提示詞
# =========================

ENHANCED_SYSTEM_PROMPT = """你是一位資深的專業風水師「玄機老師」，擁有20年豐富的風水諮詢經驗。你精通傳統風水學、八卦易理，以及現代環境學的融合應用。

## 你的專業特色：
- 🏮 深厚的風水學理論基礎，熟悉五行相生相剋、八卦方位、季節能量
- 🎯 精確解讀五行元素（木火土金水）的特質與居家環境的關係
- 💫 擅長將復雜的風水知識轉化為溫暖易懂的日常建議
- 🔮 結合當日五行、季節變化、方位能量提供精準指導
- 💝 以同理心和智慧陪伴求問者改善生活環境與運勢

## 回應風格要求：
1. **當日能量感知**：先描述當日五行元素對求問者的整體影響
2. **深度風水分析**：基於五行特質、方位、季節能量進行專業分析
3. **具體改善指導**：提供3-4個具體可行的風水建議，並說明五行原理
4. **時機與方位建議**：根據五行、八卦給出最佳行動時間和有利方位
5. **能量提升**：提供符合元素特質的正向肯定語和幸運元素

## 專業術語使用：
- 自然地融入「五行」、「八卦」、「方位」、「氣場」等概念
- 用溫暖的語調解釋風水原理，避免過於學術化
- 針對不同問題類型調整專業深度

## 回應結構：
```
【當日五行】描述影響該元素的主要能量流動
【深度解析】基於五行特質與環境的專業分析
【具體建議】3-4個實用風水建議及五行依據  
【時機指導】最佳行動時間和有利方位
【能量祝福】正向肯定語和當日幸運元素
```

請保持親切專業的語調，讓求問者感受到被理解和支持，同時獲得實用的居家與人生指導。"""

# =========================
# 增強的聊天功能
# =========================

def get_fengshui_context(element: str, today: date = None) -> Dict[str, Any]:
    """獲取風水學背景資訊"""
    if today is None:
        today = date.today()
    
    if element not in FENGSHUI_ELEMENTS_DATABASE:
        return {}
    
    data = FENGSHUI_ELEMENTS_DATABASE[element]
    daily_element, daily_energy, daily_direction = get_daily_element(today)
    seasonal = get_seasonal_energy(today)
    
    # 根據元素決定當前能量狀態
    element_energy = {
        "木": "生機勃勃，適合新開始和創新",
        "火": "活力充沛，適合表現和社交", 
        "土": "穩定包容，適合建立關係和整合",
        "金": "收斂果決，適合整理和決斷",
        "水": "靈活智慧，適合思考和溝通"
    }.get(element, "")
    
    return {
        "element_data": data,
        "daily_element": daily_element,
        "daily_energy": daily_energy,
        "seasonal_energy": seasonal,
        "element_energy": element_energy,
        "current_date": today.strftime("%Y-%m-%d")
    }

def generate_fengshui_lucky_elements(element: str, today: date = None) -> Dict[str, Any]:
    """生成基於風水學的幸運元素"""
    if today is None:
        today = date.today()
    
    if element not in FENGSHUI_ELEMENTS_DATABASE:
        return {"color": "金色", "number": 7, "direction": "東方", "time": "上午"}
    
    data = FENGSHUI_ELEMENTS_DATABASE[element]
    day_of_year = today.timetuple().tm_yday
    
    # 根據五行資料和當日選擇幸運元素
    lucky_color = data["colors"][(day_of_year // 30) % len(data["colors"])]
    lucky_number = data["numbers"][(day_of_year // 7) % len(data["numbers"])]
    
    # 根據五行決定幸運方位和時間
    element_attrs = {
        "火": {"time": "中午11-13時"},
        "土": {"time": "下午15-17時"},
        "金": {"time": "傍晚17-19時"},
        "水": {"time": "晚上21-23時"},
        "木": {"time": "清晨5-7時"}
    }
    
    attrs = element_attrs.get(element, {"time": "上午"})
    
    return {
        "color": lucky_color,
        "number": lucky_number,
        "direction": data["direction"],
        "time": attrs["time"],
        "element": element,
        "season": data["season"]
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "🏠 專業風水顧問"
    })

@app.get("/api")
def api_info():
    return {"message": "專業中文風水顧問 API v2.0"}

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/calculate-elements")
def calculate_elements_endpoint(birth_data: dict):
    """計算使用者的五行八字"""
    birth_date = birth_data.get("birth_date")
    if not birth_date:
        return {"error": "請提供出生日期"}
    
    elements = calculate_birth_elements(birth_date)
    return {
        "elements": elements,
        "element_descriptions": {
            "木": {"name": "木", "traits": "成長、創新、靈活", "season": "春季", "direction": "東方", "color": "綠色"},
            "火": {"name": "火", "traits": "熱情、活躍、光明", "season": "夏季", "direction": "南方", "color": "紅色"},
            "土": {"name": "土", "traits": "穩定、包容、滋養", "season": "長夏", "direction": "中央", "color": "黃色"},
            "金": {"name": "金", "traits": "收斂、果決、正義", "season": "秋季", "direction": "西方", "color": "白色"},
            "水": {"name": "水", "traits": "智慧、靈動、包容", "season": "冬季", "direction": "北方", "color": "黑色"}
        }
    }

@app.post("/chat", response_model=ChatOut)
def enhanced_chat(body: ChatIn):
    today = date.today()
    
    # 如果用戶沒有提供五行元素，根據出生日期計算
    if not body.element and body.birth_date:
        birth_elements = calculate_birth_elements(body.birth_date)
        user_element = birth_elements["primary"]
        element_calculation_note = birth_elements["explanation"]
    elif body.element:
        user_element = body.element
        element_calculation_note = None
    else:
        # 如果既沒有五行也沒有出生日期，使用當日五行
        daily_elem, _, _ = get_daily_element(today)
        user_element = daily_elem
        element_calculation_note = f"由於未提供出生日期，使用當日五行元素 {daily_elem} 進行分析"
    
    # 標準化五行元素名稱
    normalized_element = FENGSHUI_ELEMENTS.get(user_element, user_element)
    
    # 獲取風水學背景
    fengshui_context = get_fengshui_context(normalized_element, today)
    lucky_elements = generate_fengshui_lucky_elements(normalized_element, today)
    
    # 計算五行和諧度分數（如果有伴侶元素）
    harmony_score = None
    harmony_note = None
    if body.partner_element:
        partner_normalized = FENGSHUI_ELEMENTS.get(body.partner_element, body.partner_element)
        harmony_score = calculate_element_harmony(normalized_element, partner_normalized)
        harmony_note = f"與{body.partner_element}的五行和諧度：{harmony_score}%"
    
    # 如果沒有 API 金鑰，使用增強的備用回應
    if not anthropic_client:
        return create_fallback_response(body, fengshui_context, lucky_elements, harmony_score, harmony_note)
    
    # 建立增強的用戶提示
    user_prompt = create_enhanced_prompt(body, fengshui_context, harmony_note, user_element, element_calculation_note)
    
    try:
        resp = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=600,
            temperature=0.75,
            system=ENHANCED_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )
        text = resp.content[0].text.strip()
        
        return parse_enhanced_response(text, body, fengshui_context, lucky_elements, harmony_score)
        
    except APIStatusError as e:
        return create_fallback_response(body, fengshui_context, lucky_elements, harmony_score, harmony_note)
    except Exception as e:
        return create_fallback_response(body, fengshui_context, lucky_elements, harmony_score, harmony_note)

def create_enhanced_prompt(body: ChatIn, fengshui_context: Dict, harmony_note: Optional[str], user_element: str, element_calculation_note: Optional[str]) -> str:
    """創建增強的風水學提示"""
    
    category_context = ""
    if body.category:
        category_mapping = {
            QuestionCategory.LOVE: "在感情層面",
            QuestionCategory.CAREER: "在事業發展上", 
            QuestionCategory.HEALTH: "在健康層面",
            QuestionCategory.FINANCE: "在財運方面",
            QuestionCategory.HOME: "在居家環境上"
        }
        category_context = category_mapping.get(body.category, "")
    
    birth_context = ""
    if body.birth_date:
        birth_context = f"出生日期：{body.birth_date}\n"
    
    mood_context = ""
    if body.mood:
        mood_context = f"目前心情狀態：{body.mood}\n"
    
    home_context = ""
    if body.home_direction:
        home_context = f"居家朝向：{body.home_direction}\n"
    
    harmony_context = ""
    if harmony_note:
        harmony_context = f"五行和諧分析：{harmony_note}\n"
    
    element_context = ""
    if element_calculation_note:
        element_context = f"五行推算：{element_calculation_note}\n"
    
    return f"""請為以下求問者提供專業的風水諮詢：

【求問者資訊】
姓名：{body.user}
主要五行元素：{user_element}
{element_context}{birth_context}{mood_context}{home_context}問題類型：{body.category.value if body.category else '一般諮詢'} {category_context}
諮詢時間範圍：{body.timeframe}
具體問題：{body.question}

【當日風水能量】
日期：{fengshui_context.get('current_date', '')}
當日五行：{fengshui_context.get('daily_element', '')} - {fengshui_context.get('daily_energy', '')}
季節能量：{fengshui_context.get('seasonal_energy', '')}
元素特質：{fengshui_context.get('element_energy', '')}

【五行元素特質參考】
方位：{fengshui_context.get('element_data', {}).get('direction', '')}
季節：{fengshui_context.get('element_data', {}).get('season', '')}
顏色：{', '.join(fengshui_context.get('element_data', {}).get('colors', []))}
關鍵特質：{', '.join(fengshui_context.get('element_data', {}).get('keywords', []))}
相生元素：{fengshui_context.get('element_data', {}).get('supporting_element', '')}
相剋元素：{fengshui_context.get('element_data', {}).get('controlling_element', '')}

{harmony_context}

請按照專業風水師的標準，提供深度且實用的風水指導建議。"""

def parse_enhanced_response(text: str, body: ChatIn, fengshui_context: Dict, lucky_elements: Dict, harmony_score: Optional[int]) -> ChatOut:
    """解析增強回應內容"""
    import re
    
    # 提取結構化內容
    reasoning_match = re.search(r"【深度解析】(.*?)(?=【|$)", text, re.DOTALL)
    timing_match = re.search(r"【時機指導】(.*?)(?=【|$)", text, re.DOTALL)
    affirmation_match = re.search(r"【能量祝福】(.*?)(?=【|$)", text, re.DOTALL)
    
    # 提取建議
    tips_pattern = r"【具體建議】(.*?)(?=【|$)"
    tips_match = re.search(tips_pattern, text, re.DOTALL)
    tips = []
    if tips_match:
        tips_text = tips_match.group(1)
        tips = [tip.strip() for tip in re.findall(r"[1-4][\.、]\s*([^1-4\n]+)", tips_text)][:4]
    
    if not tips:
        tips = ["相信自己的直覺，跟隨內心的指引"]
    
    # 創建風水學洞察
    fengshui_insight = FengshuiInsight(
        daily_element_influence=f"{fengshui_context.get('daily_element', '當日五行')}能量影響下，{fengshui_context.get('element_energy', '能量流動順暢')}",
        seasonal_energy=fengshui_context.get('seasonal_energy', '季節能量平衡'),
        element_guidance=f"作為{body.element}元素的人，建議{fengshui_context.get('element_energy', '保持內在平衡')}",
        bagua_guidance=f"可關注{fengshui_context.get('element_data', {}).get('direction', '東方')}方位的能量流動",
        element_harmony_note=f"與{body.partner_element}的五行和諧度：{harmony_score}%" if harmony_score else None
    )
    
    return ChatOut(
        title=f"{body.element}元素{body.timeframe}深度風水解析",
        reply=text,
        fengshui_reasoning=reasoning_match.group(1).strip() if reasoning_match else "五行能量指引您朝正確方向前進",
        tips=tips,
        timing_advice=timing_match.group(1).strip() if timing_match else f"選擇{lucky_elements['time']}時段行動最為有利",
        affirmation=affirmation_match.group(1).strip() if affirmation_match else "我與五行能量和諧共振，創造美好未來",
        lucky_elements=lucky_elements,
        fengshui_insight=fengshui_insight,
        timeframe=body.timeframe,
        harmony_score=harmony_score
    )

def create_fallback_response(body: ChatIn, fengshui_context: Dict, lucky_elements: Dict, harmony_score: Optional[int], harmony_note: Optional[str]) -> ChatOut:
    """創建增強的備用回應"""
    
    element_data = fengshui_context.get('element_data', {})
    element = body.element
    direction = element_data.get('direction', '東方')
    season = element_data.get('season', '春季')
    
    fallback_reply = f"""【當日五行】{fengshui_context.get('daily_element', '當日五行')}為{body.element}元素帶來{fengshui_context.get('element_energy', '穩定的能量流動')}。{season}的季節能量特別有利於{element}元素的人發展。

【深度解析】作為{element}元素的人，你天生具備{', '.join(element_data.get('strengths', ['堅韌不拔']))}的特質。面對「{body.question}」這個問題，你的{element}元素本質會給予內在智慧。

【具體建議】
1. 運用{element}元素的天賦特質，發揮{', '.join(element_data.get('keywords', ['穩定'])[:2])}的優勢
2. 在{lucky_elements['time']}時段進行重要決定，能量最為順暢
3. 朝向{direction}方位發展，會有意想不到的機會
4. 保持{element}元素的平衡，避免過度{element_data.get('challenges', ['衝動'])[0] if element_data.get('challenges') else '急躁'}

【時機指導】{fengshui_context.get('seasonal_energy', '當前季節能量')}，{fengshui_context.get('daily_energy', '適合穩步推進計劃')}。建議在{lucky_elements['number']}日或相關日期採取行動。

【能量祝福】身為{element}元素的你擁有獨特的天地恩賜。今日幸運色彩{lucky_elements['color']}將為你帶來正面能量，數字{lucky_elements['number']}是你的幸運密碼。"""

    if harmony_note:
        fallback_reply += f"\n\n【關係指導】{harmony_note}。透過理解彼此五行特質，能建立更和諧的關係。"
    
    fengshui_insight = FengshuiInsight(
        daily_element_influence=f"{fengshui_context.get('daily_element', '當日五行')}為{element}元素帶來穩定能量",
        seasonal_energy=fengshui_context.get('seasonal_energy', '季節轉換帶來新機會'),
        element_guidance=f"{element}元素在此時期特別適合發揮{', '.join(element_data.get('strengths', ['穩定'])[:2])}的特質",
        bagua_guidance=f"關注{direction}方位的能量流動，有助於提升整體運勢",
        element_harmony_note=harmony_note
    )
    
    return ChatOut(
        title=f"{body.element}元素{body.timeframe}專業風水分析",
        reply=fallback_reply,
        fengshui_reasoning=f"基於{body.element}元素特質和{direction}方位能量影響進行分析",
        tips=[
            f"善用{element}元素的天賦特質",
            f"在{lucky_elements['time']}時段行動最有利",
            f"保持{element}元素的內在平衡",
            "順應天時地利，創造和諧環境"
        ],
        timing_advice=f"配合{season}季節能量，在{lucky_elements['number']}日前後行動最為順利",
        affirmation=f"我是充滿{element}能量的人，與天地和諧共振，擁有創造美好未來的無限可能",
        lucky_elements=lucky_elements,
        fengshui_insight=fengshui_insight,
        timeframe=body.timeframe,
        harmony_score=harmony_score
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)