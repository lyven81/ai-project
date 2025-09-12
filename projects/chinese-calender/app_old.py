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
    title="專業中文星座顧問",
    version="2.0.0",
    description="基於傳統占星學原理的智慧星座顧問，提供深度個人化建議"
)

# 設定模板
templates = Jinja2Templates(directory=".")

# =========================
# 占星學知識庫系統
# =========================

class Element(Enum):
    FIRE = "火"
    EARTH = "土"
    AIR = "風"
    WATER = "水"

class Modality(Enum):
    CARDINAL = "基本"
    FIXED = "固定"
    MUTABLE = "變動"

class QuestionCategory(Enum):
    LOVE = "感情"
    CAREER = "事業"
    HEALTH = "健康"
    GENERAL = "綜合"
    FINANCE = "財運"
    STUDY = "學習"

# 詳細星座資料庫
ZODIAC_DATABASE = {
    "牡羊座": {
        "english": "Aries",
        "dates": (3, 21, 4, 19),
        "element": Element.FIRE,
        "modality": Modality.CARDINAL,
        "ruling_planet": "火星",
        "keywords": ["積極", "領導", "衝動", "勇敢", "開創"],
        "strengths": ["領導力強", "行動力佳", "勇於嘗試", "熱情洋溢"],
        "challenges": ["容易衝動", "缺乏耐心", "過於直接"],
        "compatible_signs": ["獅子座", "射手座", "雙子座", "水瓶座"],
        "colors": ["紅色", "橙色", "金色"],
        "lucky_numbers": [1, 8, 17, 26],
        "body_parts": ["頭部", "大腦", "眼睛"]
    },
    "金牛座": {
        "english": "Taurus",
        "dates": (4, 20, 5, 20),
        "element": Element.EARTH,
        "modality": Modality.FIXED,
        "ruling_planet": "金星",
        "keywords": ["穩定", "實際", "美感", "固執", "享受"],
        "strengths": ["穩重可靠", "藝術天份", "理財能力", "堅持不懈"],
        "challenges": ["過於固執", "變化適應慢", "物質主義"],
        "compatible_signs": ["處女座", "摩羯座", "巨蟹座", "雙魚座"],
        "colors": ["綠色", "粉色", "藍色"],
        "lucky_numbers": [2, 6, 15, 24],
        "body_parts": ["頸部", "喉嚨", "聲帶"]
    },
    "雙子座": {
        "english": "Gemini",
        "dates": (5, 21, 6, 20),
        "element": Element.AIR,
        "modality": Modality.MUTABLE,
        "ruling_planet": "水星",
        "keywords": ["好奇", "溝通", "多變", "聰明", "適應"],
        "strengths": ["溝通能力強", "學習快速", "適應力佳", "思維敏捷"],
        "challenges": ["注意力分散", "缺乏專注", "善變"],
        "compatible_signs": ["天秤座", "水瓶座", "牡羊座", "獅子座"],
        "colors": ["黃色", "銀色", "白色"],
        "lucky_numbers": [3, 12, 21, 30],
        "body_parts": ["手臂", "肺部", "神經系統"]
    },
    "巨蟹座": {
        "english": "Cancer",
        "dates": (6, 21, 7, 22),
        "element": Element.WATER,
        "modality": Modality.CARDINAL,
        "ruling_planet": "月亮",
        "keywords": ["情感", "家庭", "保護", "直覺", "母性"],
        "strengths": ["直覺力強", "照顧他人", "情感豐富", "忠誠"],
        "challenges": ["情緒波動", "過於敏感", "依賴性強"],
        "compatible_signs": ["天蠍座", "雙魚座", "金牛座", "處女座"],
        "colors": ["銀色", "白色", "海藍色"],
        "lucky_numbers": [4, 13, 22, 31],
        "body_parts": ["胸部", "胃部", "子宮"]
    },
    "獅子座": {
        "english": "Leo",
        "dates": (7, 23, 8, 22),
        "element": Element.FIRE,
        "modality": Modality.FIXED,
        "ruling_planet": "太陽",
        "keywords": ["自信", "創造", "表演", "慷慨", "領導"],
        "strengths": ["自信魅力", "創造力強", "慷慨大方", "領導天份"],
        "challenges": ["過於自我", "愛面子", "固執己見"],
        "compatible_signs": ["牡羊座", "射手座", "雙子座", "天秤座"],
        "colors": ["金色", "橙色", "紫色"],
        "lucky_numbers": [5, 14, 23, 32],
        "body_parts": ["心臟", "脊椎", "背部"]
    },
    "處女座": {
        "english": "Virgo",
        "dates": (8, 23, 9, 22),
        "element": Element.EARTH,
        "modality": Modality.MUTABLE,
        "ruling_planet": "水星",
        "keywords": ["完美", "分析", "服務", "實用", "健康"],
        "strengths": ["注重細節", "分析能力", "服務精神", "追求完美"],
        "challenges": ["過度挑剔", "焦慮傾向", "缺乏自信"],
        "compatible_signs": ["金牛座", "摩羯座", "巨蟹座", "天蠍座"],
        "colors": ["深綠色", "褐色", "海軍藍"],
        "lucky_numbers": [6, 15, 24, 33],
        "body_parts": ["腹部", "腸道", "消化系統"]
    },
    "天秤座": {
        "english": "Libra",
        "dates": (9, 23, 10, 22),
        "element": Element.AIR,
        "modality": Modality.CARDINAL,
        "ruling_planet": "金星",
        "keywords": ["平衡", "和諧", "美感", "合作", "公正"],
        "strengths": ["外交手腕", "審美能力", "公平正義", "合作精神"],
        "challenges": ["優柔寡斷", "依賴他人", "逃避衝突"],
        "compatible_signs": ["雙子座", "水瓶座", "獅子座", "射手座"],
        "colors": ["粉色", "淺藍色", "薄荷綠"],
        "lucky_numbers": [7, 16, 25, 34],
        "body_parts": ["腎臟", "腰部", "皮膚"]
    },
    "天蠍座": {
        "english": "Scorpio",
        "dates": (10, 23, 11, 21),
        "element": Element.WATER,
        "modality": Modality.FIXED,
        "ruling_planet": "冥王星",
        "keywords": ["深度", "轉化", "神秘", "強度", "洞察"],
        "strengths": ["洞察力強", "意志堅定", "神秘魅力", "轉化能力"],
        "challenges": ["占有慾強", "報復心重", "極端傾向"],
        "compatible_signs": ["巨蟹座", "雙魚座", "處女座", "摩羯座"],
        "colors": ["深紅色", "黑色", "酒紅色"],
        "lucky_numbers": [8, 17, 26, 35],
        "body_parts": ["生殖器官", "排泄系統"]
    },
    "射手座": {
        "english": "Sagittarius",
        "dates": (11, 22, 12, 21),
        "element": Element.FIRE,
        "modality": Modality.MUTABLE,
        "ruling_planet": "木星",
        "keywords": ["自由", "探索", "哲學", "樂觀", "冒險"],
        "strengths": ["樂觀開朗", "哲學思維", "冒險精神", "國際視野"],
        "challenges": ["缺乏耐心", "承諾恐懼", "過於直接"],
        "compatible_signs": ["牡羊座", "獅子座", "天秤座", "水瓶座"],
        "colors": ["紫色", "深藍色", "栗色"],
        "lucky_numbers": [9, 18, 27, 36],
        "body_parts": ["大腿", "臀部", "肝臟"]
    },
    "摩羯座": {
        "english": "Capricorn",
        "dates": (12, 22, 1, 19),
        "element": Element.EARTH,
        "modality": Modality.CARDINAL,
        "ruling_planet": "土星",
        "keywords": ["責任", "成就", "傳統", "耐心", "權威"],
        "strengths": ["責任感強", "堅持不懈", "組織能力", "實現目標"],
        "challenges": ["過於嚴肅", "壓力大", "缺乏彈性"],
        "compatible_signs": ["金牛座", "處女座", "天蠍座", "雙魚座"],
        "colors": ["黑色", "深褐色", "墨綠色"],
        "lucky_numbers": [10, 19, 28, 37],
        "body_parts": ["膝蓋", "骨骼", "牙齒"]
    },
    "水瓶座": {
        "english": "Aquarius",
        "dates": (1, 20, 2, 18),
        "element": Element.AIR,
        "modality": Modality.FIXED,
        "ruling_planet": "天王星",
        "keywords": ["創新", "獨立", "人道", "未來", "友誼"],
        "strengths": ["創新思維", "獨立自主", "人道主義", "友善開放"],
        "challenges": ["情感疏離", "固執己見", "反叛傾向"],
        "compatible_signs": ["雙子座", "天秤座", "牡羊座", "射手座"],
        "colors": ["藍色", "青色", "電光藍"],
        "lucky_numbers": [11, 20, 29, 38],
        "body_parts": ["小腿", "踝部", "循環系統"]
    },
    "雙魚座": {
        "english": "Pisces",
        "dates": (2, 19, 3, 20),
        "element": Element.WATER,
        "modality": Modality.MUTABLE,
        "ruling_planet": "海王星",
        "keywords": ["直覺", "慈悲", "藝術", "靈性", "夢想"],
        "strengths": ["直覺敏銳", "富有同情心", "藝術天份", "適應力強"],
        "challenges": ["過於敏感", "逃避現實", "缺乏界限"],
        "compatible_signs": ["巨蟹座", "天蠍座", "金牛座", "摩羯座"],
        "colors": ["海綠色", "淺紫色", "銀白色"],
        "lucky_numbers": [12, 21, 30, 39],
        "body_parts": ["腳部", "淋巴系統"]
    }
}

# 星座對應（加入別名支持）
ZODIAC_SIGNS = {
    "牡羊座": "牡羊座", "白羊座": "牡羊座",
    "金牛座": "金牛座",
    "雙子座": "雙子座",
    "巨蟹座": "巨蟹座",
    "獅子座": "獅子座",
    "處女座": "處女座",
    "天秤座": "天秤座", "天平座": "天秤座",
    "天蠍座": "天蠍座", "天蝎座": "天蠍座",
    "射手座": "射手座",
    "摩羯座": "摩羯座", "山羊座": "摩羊座",
    "水瓶座": "水瓶座",
    "雙魚座": "雙魚座"
}

# =========================
# 月相和天象計算
# =========================

def get_lunar_phase(today: date = None) -> Tuple[str, str, float]:
    """計算當前月相"""
    if today is None:
        today = date.today()
    
    # 簡化的月相計算（基於農曆周期）
    reference_new_moon = date(2024, 1, 11)  # 參考新月日期
    days_since = (today - reference_new_moon).days
    lunar_cycle = 29.53  # 月相周期
    phase_position = (days_since % lunar_cycle) / lunar_cycle
    
    if phase_position < 0.125:
        phase = "新月"
        energy = "新開始的能量，適合許願和規劃"
    elif phase_position < 0.375:
        phase = "上弦月"
        energy = "行動力強化，適合積極推進計劃"
    elif phase_position < 0.625:
        phase = "滿月"
        energy = "情感和直覺力高漲，注意情緒平衡"
    elif phase_position < 0.875:
        phase = "下弦月"
        energy = "釋放和淨化，適合整理和反思"
    else:
        phase = "新月"
        energy = "新開始的能量，適合許願和規劃"
    
    return phase, energy, phase_position

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

def calculate_compatibility_score(sign1: str, sign2: str) -> int:
    """計算星座相容性分數"""
    if sign1 not in ZODIAC_DATABASE or sign2 not in ZODIAC_DATABASE:
        return 50
    
    data1 = ZODIAC_DATABASE[sign1]
    data2 = ZODIAC_DATABASE[sign2]
    
    score = 50
    
    # 元素相容性
    if data1["element"] == data2["element"]:
        score += 20
    elif (data1["element"] in [Element.FIRE, Element.AIR] and 
          data2["element"] in [Element.FIRE, Element.AIR]) or \
         (data1["element"] in [Element.EARTH, Element.WATER] and 
          data2["element"] in [Element.EARTH, Element.WATER]):
        score += 10
    
    # 相容星座列表
    if sign2 in data1["compatible_signs"]:
        score += 25
    
    # 模式相容性
    if data1["modality"] != data2["modality"]:
        score += 5
    
    return min(95, max(15, score))

# =========================
# 增強的資料模型
# =========================

class ChatIn(BaseModel):
    user: str = Field(..., description="用戶姓名")
    sign: str = Field(..., description="星座名稱（中文）")
    question: str = Field(..., description="想要諮詢的問題")
    category: Optional[QuestionCategory] = Field(None, description="問題類型")
    birth_date: Optional[str] = Field(None, description="出生日期 YYYY-MM-DD（可選，用於更精確分析）")
    timeframe: Optional[str] = Field("今天", description="時間範圍：今天、本週、本月")
    mood: Optional[str] = Field(None, description="當前心情或能量狀態")
    partner_sign: Optional[str] = Field(None, description="伴侶星座（感情問題時）")

class AstrologicalInsight(BaseModel):
    current_planetary_influence: str
    lunar_phase_effect: str
    seasonal_energy: str
    element_guidance: str
    compatibility_note: Optional[str] = None

class ChatOut(BaseModel):
    title: str
    reply: str
    astrological_reasoning: str
    tips: List[str]
    timing_advice: str
    affirmation: str
    lucky_elements: Dict[str, Any]
    astrological_insight: AstrologicalInsight
    timeframe: str
    compatibility_score: Optional[int] = None

# =========================
# 專業占星學系統提示詞
# =========================

ENHANCED_SYSTEM_PROMPT = """你是一位資深的專業占星師「星辰老師」，擁有15年豐富的占星諮詢經驗。你精通傳統占星學、心理占星學，以及中國古典星象學的融合應用。

## 你的專業特色：
- 🌟 深厚的占星學理論基礎，熟悉行星運行、月相變化、季節能量
- 🎯 精確解讀十二星座的元素屬性（火土風水）、模式特質（基本固定變動）
- 💫 擅長將復雜的占星知識轉化為溫暖易懂的日常建議
- 🔮 結合當前天象、月相、季節能量提供精準時機指導
- 💝 以同理心和智慧陪伴求問者面對人生課題

## 回應風格要求：
1. **開場氣場感知**：先描述當前天象對該星座的整體影響
2. **深度占星分析**：基於星座特質、守護星、元素屬性進行專業分析
3. **具體行動指導**：提供3-4個具體可行的建議，並說明占星學依據
4. **時機建議**：根據月相、行星運行給出最佳行動時間
5. **能量提升**：提供符合星座特質的正向肯定語和幸運元素

## 專業術語使用：
- 自然地融入「守護星」、「元素能量」、「宮位」、「相位」等概念
- 用溫暖的語調解釋占星原理，避免過於學術化
- 針對不同問題類型調整專業深度

## 回應結構：
```
【當前天象】描述影響該星座的主要行星能量
【深度解析】基於星座特質的專業分析
【具體建議】3-4個實用建議及占星依據  
【時機指導】最佳行動時間和需要注意的時期
【能量祝福】正向肯定語和當日幸運元素
```

請保持親切專業的語調，讓求問者感受到被理解和支持，同時獲得實用的人生指導。"""

# =========================
# 增強的聊天功能
# =========================

def get_astrological_context(sign: str, today: date = None) -> Dict[str, Any]:
    """獲取占星學背景資訊"""
    if today is None:
        today = date.today()
    
    if sign not in ZODIAC_DATABASE:
        return {}
    
    data = ZODIAC_DATABASE[sign]
    lunar_phase, lunar_energy, phase_pos = get_lunar_phase(today)
    seasonal = get_seasonal_energy(today)
    
    # 根據元素決定當前能量狀態
    element_energy = {
        Element.FIRE: "活力充沛，適合主動出擊",
        Element.EARTH: "務實穩重，適合踏實行動", 
        Element.AIR: "思維活躍，適合溝通交流",
        Element.WATER: "直覺敏銳，適合情感表達"
    }.get(data["element"], "")
    
    return {
        "sign_data": data,
        "lunar_phase": lunar_phase,
        "lunar_energy": lunar_energy,
        "seasonal_energy": seasonal,
        "element_energy": element_energy,
        "current_date": today.strftime("%Y-%m-%d")
    }

def generate_lucky_elements(sign: str, today: date = None) -> Dict[str, Any]:
    """生成基於占星學的幸運元素"""
    if today is None:
        today = date.today()
    
    if sign not in ZODIAC_DATABASE:
        return {"color": "金色", "number": 7, "direction": "東方", "time": "上午"}
    
    data = ZODIAC_DATABASE[sign]
    day_of_year = today.timetuple().tm_yday
    
    # 根據星座資料和當日選擇幸運元素
    lucky_color = data["colors"][(day_of_year // 30) % len(data["colors"])]
    lucky_number = data["lucky_numbers"][(day_of_year // 7) % len(data["lucky_numbers"])]
    
    # 根據元素決定幸運方位和時間
    element_attrs = {
        Element.FIRE: {"direction": "南方", "time": "中午"},
        Element.EARTH: {"direction": "西方", "time": "傍晚"},
        Element.AIR: {"direction": "東方", "time": "上午"},
        Element.WATER: {"direction": "北方", "time": "夜晚"}
    }
    
    attrs = element_attrs.get(data["element"], {"direction": "東方", "time": "上午"})
    
    return {
        "color": lucky_color,
        "number": lucky_number,
        "direction": attrs["direction"],
        "time": attrs["time"],
        "element": data["element"].value
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "🔮 專業星座顧問"
    })

@app.get("/api")
def api_info():
    return {"message": "專業中文星座顧問 API v2.0"}

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatOut)
def enhanced_chat(body: ChatIn):
    today = date.today()
    
    # 標準化星座名稱
    normalized_sign = ZODIAC_SIGNS.get(body.sign, body.sign)
    
    # 獲取占星學背景
    astro_context = get_astrological_context(normalized_sign, today)
    lucky_elements = generate_lucky_elements(normalized_sign, today)
    
    # 計算相容性分數（如果有伴侶星座）
    compatibility_score = None
    compatibility_note = None
    if body.partner_sign:
        partner_normalized = ZODIAC_SIGNS.get(body.partner_sign, body.partner_sign)
        compatibility_score = calculate_compatibility_score(normalized_sign, partner_normalized)
        compatibility_note = f"與{body.partner_sign}的相容性指數：{compatibility_score}%"
    
    # 如果沒有 API 金鑰，使用增強的備用回應
    if not anthropic_client:
        return create_fallback_response(body, astro_context, lucky_elements, compatibility_score, compatibility_note)
    
    # 建立增強的用戶提示
    user_prompt = create_enhanced_prompt(body, astro_context, compatibility_note)
    
    try:
        resp = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=600,
            temperature=0.75,
            system=ENHANCED_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )
        text = resp.content[0].text.strip()
        
        return parse_enhanced_response(text, body, astro_context, lucky_elements, compatibility_score)
        
    except APIStatusError as e:
        return create_fallback_response(body, astro_context, lucky_elements, compatibility_score, compatibility_note)
    except Exception as e:
        return create_fallback_response(body, astro_context, lucky_elements, compatibility_score, compatibility_note)

def create_enhanced_prompt(body: ChatIn, astro_context: Dict, compatibility_note: Optional[str]) -> str:
    """創建增強的占星學提示"""
    
    category_context = ""
    if body.category:
        category_mapping = {
            QuestionCategory.LOVE: "在感情層面",
            QuestionCategory.CAREER: "在事業發展上", 
            QuestionCategory.HEALTH: "在健康層面",
            QuestionCategory.FINANCE: "在財運方面",
            QuestionCategory.STUDY: "在學習成長上"
        }
        category_context = category_mapping.get(body.category, "")
    
    birth_context = ""
    if body.birth_date:
        birth_context = f"出生日期：{body.birth_date}\n"
    
    mood_context = ""
    if body.mood:
        mood_context = f"目前心情狀態：{body.mood}\n"
    
    compatibility_context = ""
    if compatibility_note:
        compatibility_context = f"相容性分析：{compatibility_note}\n"
    
    return f"""請為以下求問者提供專業的占星諮詢：

【求問者資訊】
姓名：{body.user}
星座：{body.sign}
{birth_context}{mood_context}問題類型：{body.category.value if body.category else '一般諮詢'} {category_context}
諮詢時間範圍：{body.timeframe}
具體問題：{body.question}

【當前天象資訊】
日期：{astro_context.get('current_date', '')}
月相：{astro_context.get('lunar_phase', '')} - {astro_context.get('lunar_energy', '')}
季節能量：{astro_context.get('seasonal_energy', '')}
星座元素特質：{astro_context.get('element_energy', '')}

【星座特質參考】
守護星：{astro_context.get('sign_data', {}).get('ruling_planet', '')}
元素：{astro_context.get('sign_data', {}).get('element', '').value if astro_context.get('sign_data') else ''}
模式：{astro_context.get('sign_data', {}).get('modality', '').value if astro_context.get('sign_data') else ''}
關鍵特質：{', '.join(astro_context.get('sign_data', {}).get('keywords', []))}

{compatibility_context}

請按照專業占星師的標準，提供深度且實用的指導建議。"""

def parse_enhanced_response(text: str, body: ChatIn, astro_context: Dict, lucky_elements: Dict, compatibility_score: Optional[int]) -> ChatOut:
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
    
    # 創建占星學洞察
    astrological_insight = AstrologicalInsight(
        current_planetary_influence=f"{astro_context.get('sign_data', {}).get('ruling_planet', '守護星')}的影響下，{astro_context.get('element_energy', '能量流動順暢')}",
        lunar_phase_effect=f"{astro_context.get('lunar_phase', '月相')}帶來{astro_context.get('lunar_energy', '穩定能量')}",
        seasonal_energy=astro_context.get('seasonal_energy', '季節能量平衡'),
        element_guidance=f"作為{astro_context.get('sign_data', {}).get('element', Element.FIRE).value}元素星座，建議{astro_context.get('element_energy', '保持內在平衡')}",
        compatibility_note=f"與{body.partner_sign}的相容性：{compatibility_score}%" if compatibility_score else None
    )
    
    return ChatOut(
        title=f"{body.sign}{body.timeframe}深度運勢解析",
        reply=text,
        astrological_reasoning=reasoning_match.group(1).strip() if reasoning_match else "星座能量指引您朝正確方向前進",
        tips=tips,
        timing_advice=timing_match.group(1).strip() if timing_match else f"選擇{lucky_elements['time']}時段行動最為有利",
        affirmation=affirmation_match.group(1).strip() if affirmation_match else "我與宇宙能量和諧共振，創造美好未來",
        lucky_elements=lucky_elements,
        astrological_insight=astrological_insight,
        timeframe=body.timeframe,
        compatibility_score=compatibility_score
    )

def create_fallback_response(body: ChatIn, astro_context: Dict, lucky_elements: Dict, compatibility_score: Optional[int], compatibility_note: Optional[str]) -> ChatOut:
    """創建增強的備用回應"""
    
    sign_data = astro_context.get('sign_data', {})
    element = sign_data.get('element', Element.FIRE).value
    ruling_planet = sign_data.get('ruling_planet', '守護星')
    
    fallback_reply = f"""【當前天象】{ruling_planet}為{body.sign}帶來{astro_context.get('element_energy', '穩定的能量流動')}。{astro_context.get('lunar_phase', '當前月相')}特別有利於{element}元素星座的發展。

【深度解析】作為{element}元素的{body.sign}，你天生具備{', '.join(sign_data.get('strengths', ['堅韌不拔']))}的特質。面對「{body.question}」這個問題，你的{ruling_planet}守護力量會給予內在智慧。

【具體建議】
1. 運用{body.sign}的直覺力，相信第一印象的判斷
2. 在{lucky_elements['time']}時段進行重要決定，能量最為順暢
3. 朝向{lucky_elements['direction']}發展，會有意想不到的機會
4. 保持{element}元素的平衡，避免過度{sign_data.get('challenges', ['衝動'])[0] if sign_data.get('challenges') else '急躁'}

【時機指導】{astro_context.get('seasonal_energy', '當前季節能量')}，{astro_context.get('lunar_energy', '適合穩步推進計劃')}。建議在{lucky_elements['number']}日或相關日期採取行動。

【能量祝福】身為{body.sign}的你擁有獨特的宇宙恩賜。今日幸運色彩{lucky_elements['color']}將為你帶來正面能量，數字{lucky_elements['number']}是你的幸運密碼。"""

    if compatibility_note:
        fallback_reply += f"\n\n【關係指導】{compatibility_note}。透過理解彼此星座特質，能建立更和諧的關係。"
    
    astrological_insight = AstrologicalInsight(
        current_planetary_influence=f"{ruling_planet}帶來{element}元素的穩定能量",
        lunar_phase_effect=astro_context.get('lunar_energy', '月相能量平衡'),
        seasonal_energy=astro_context.get('seasonal_energy', '季節轉換帶來新機會'),
        element_guidance=f"{element}元素星座在此時期特別適合內省和規劃",
        compatibility_note=compatibility_note
    )
    
    return ChatOut(
        title=f"{body.sign}{body.timeframe}專業運勢分析",
        reply=fallback_reply,
        astrological_reasoning=f"基於{body.sign}的{element}元素特質和{ruling_planet}守護影響進行分析",
        tips=[
            f"善用{body.sign}的天賦直覺",
            f"在{lucky_elements['time']}時段行動最有利",
            f"保持{element}元素的內在平衡",
            "相信宇宙的安排和指引"
        ],
        timing_advice=f"配合{astro_context.get('lunar_phase', '月相')}能量，在{lucky_elements['number']}日前後行動最為順利",
        affirmation=f"我是充滿{element}能量的{body.sign}，擁有創造美好未來的無限可能",
        lucky_elements=lucky_elements,
        astrological_insight=astrological_insight,
        timeframe=body.timeframe,
        compatibility_score=compatibility_score
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)