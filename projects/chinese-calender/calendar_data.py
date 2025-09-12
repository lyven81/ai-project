import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import random
from lunar_python import Solar

# 生肖对应
ZODIAC_ANIMALS = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 二十四节气
SOLAR_TERMS = [
    "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑", 
    "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"
]

# 天干地支
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 宜事项库
YI_ITEMS = {
    "嫁娶": "结婚典礼",
    "纳采": "下聘礼", 
    "开市": "开业营业",
    "交易": "买卖交易",
    "立券": "签订合约",
    "入宅": "搬家入住",
    "移徙": "迁移居所",
    "安床": "安置床铺",
    "出行": "外出旅行",
    "祭祀": "祭拜先祖",
    "祈福": "祈求福运",
    "求嗣": "求子祈嗣",
    "上梁": "建筑上梁",
    "动土": "开始建设",
    "破土": "开始动工",
    "修造": "装修建造",
    "栽种": "种植作物",
    "收获": "收割庄稼",
    "纳财": "进财招财",
    "开仓": "开启仓库",
    "牧养": "饲养牲畜",
    "造车器": "制造器具",
    "经络": "针灸治疗",
    "裁衣": "制作衣物",
    "冠笄": "成人礼仪",
    "会亲友": "聚会社交"
}

# 忌事项库  
JI_ITEMS = {
    "嫁娶": "结婚典礼",
    "入宅": "搬家入住", 
    "开市": "开业营业",
    "动土": "开始建设",
    "破土": "开始动工",
    "出行": "外出旅行",
    "安葬": "埋葬逝者",
    "修造": "装修建造",
    "拆卸": "拆除建筑",
    "栽种": "种植作物",
    "伐木": "砍伐树木",
    "开仓": "开启仓库",
    "出货财": "支出财物",
    "纳畜": "购买牲畜",
    "造桥": "建造桥梁",
    "作灶": "建造厨房",
    "开池": "挖掘池塘",
    "掘井": "挖掘水井",
    "针灸": "针灸治疗",
    "理发": "剪发美容",
    "整手足甲": "修剪指甲",
    "沐浴": "洗浴清洁",
    "扫舍": "打扫房屋",
    "破屋": "拆除房屋",
    "坏垣": "拆除围墙"
}

# 用途与宜事项的映射
PURPOSE_MAPPING = {
    "marriage": ["嫁娶", "纳采", "祭祀", "祈福", "会亲友"],
    "move": ["入宅", "移徙", "安床", "祭祀", "祈福"],
    "opening": ["开市", "立券", "交易", "纳财", "祭祀"],
    "contract": ["立券", "交易", "开市", "纳财"],
    "travel": ["出行", "祈福", "祭祀"],
    "groundbreaking": ["动土", "破土", "上梁", "修造", "祭祀"]
}

def get_zodiac_animal(year: int) -> str:
    """根据年份获取生肖（以1900年为鼠年基准）"""
    return ZODIAC_ANIMALS[(year - 1900) % 12]

# 使用 lunar-python 提供的精准农历和节气

def get_lunar_date(date_obj: date) -> str:
    """
    返回形如：'乙巳年七月十五'
    """
    solar = Solar.fromYmd(date_obj.year, date_obj.month, date_obj.day)
    lunar = solar.getLunar()
    ganzhi_year = lunar.getYearInGanZhi()        # 乙巳
    month_cn   = lunar.getMonthInChinese()       # 七
    day_cn     = lunar.getDayInChinese()         # 十五
    return f"{ganzhi_year}年{month_cn}月{day_cn}"

def get_day_zodiac(date_obj: date) -> str:
    """
    当日生肖（按农历年），例如：'蛇'
    """
    solar = Solar.fromYmd(date_obj.year, date_obj.month, date_obj.day)
    lunar = solar.getLunar()
    return lunar.getYearShengXiao()

def get_solar_term(date_obj: date) -> str | None:
    """
    返回当天节气名（若无则 None）
    """
    solar = Solar.fromYmd(date_obj.year, date_obj.month, date_obj.day)
    lunar = solar.getLunar()
    return lunar.getJieQi() or None


def generate_yi_ji_items(date_obj: date) -> tuple[List[str], List[str]]:
    """生成宜忌事项（基于简化的五行和天干地支理论）"""
    random.seed(date_obj.toordinal())  # 使用日期作为种子，保证一致性
    
    # 根据日期特征决定宜忌倾向
    day_of_week = date_obj.weekday()
    day_of_month = date_obj.day
    
    # 选择宜事项（3-6个）
    yi_count = random.randint(3, 6)
    yi_keys = random.sample(list(YI_ITEMS.keys()), yi_count)
    yi_list = [f"{key}（{YI_ITEMS[key]}）" for key in yi_keys]
    
    # 选择忌事项（3-6个），避免与宜事项冲突
    available_ji = {k: v for k, v in JI_ITEMS.items() if k not in yi_keys}
    ji_count = random.randint(3, 6)
    ji_keys = random.sample(list(available_ji.keys()), min(ji_count, len(available_ji)))
    ji_list = [f"{key}（{available_ji[key]}）" for key in ji_keys]
    
    return yi_list, ji_list

def get_chong_zodiac(date_obj: date) -> str:
    """获取冲煞生肖"""
    day_zodiac = get_day_zodiac(date_obj)
    day_zodiac_index = ZODIAC_ANIMALS.index(day_zodiac)
    # 相冲关系：鼠马、牛羊、虎猴、兔鸡、龙狗、蛇猪
    chong_index = (day_zodiac_index + 6) % 12
    return ZODIAC_ANIMALS[chong_index]

def generate_notes(date_obj: date, yi: List[str], ji: List[str]) -> str:
    """生成简明解释"""
    day_zodiac = get_day_zodiac(date_obj)
    chong_zodiac = get_chong_zodiac(date_obj)
    
    # 提取主要宜忌事项
    main_yi = [item.split("（")[0] for item in yi[:2]]
    main_ji = [item.split("（")[0] for item in ji[:2]]
    
    notes = f"今日为{day_zodiac}日，冲{chong_zodiac}。"
    notes += f"宜{','.join(main_yi)}等事；"
    notes += f"忌{','.join(main_ji)}等事。"
    notes += "谨慎行事，择时而动。"
    
    return notes

def generate_calendar_data(start_date: date, days_count: int = 90) -> List[Dict[str, Any]]:
    """生成日历数据"""
    calendar_data = []
    
    for i in range(days_count):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        lunar_date = get_lunar_date(current_date)
        zodiac_of_day = get_day_zodiac(current_date)
        solar_term = get_solar_term(current_date)
        yi, ji = generate_yi_ji_items(current_date)
        chong_zodiac = get_chong_zodiac(current_date)
        notes = generate_notes(current_date, yi, ji)
        
        day_data = {
            "id": date_str,
            "lunar_date": lunar_date,
            "zodiac_of_day": zodiac_of_day,
            "solar_term": solar_term,
            "yi": yi,
            "ji": ji,
            "chong_zodiac": chong_zodiac,
            "notes": notes
        }
        
        calendar_data.append(day_data)
    
    return calendar_data

def is_good_day_for_purpose(day_data: Dict[str, Any], purpose: str) -> bool:
    """判断某日是否适合特定用途"""
    if purpose not in PURPOSE_MAPPING:
        return False
    
    required_items = PURPOSE_MAPPING[purpose]
    yi_items = [item.split("（")[0] for item in day_data["yi"]]
    ji_items = [item.split("（")[0] for item in day_data["ji"]]
    
    # 检查是否包含所需的宜事项
    has_good_items = any(item in yi_items for item in required_items)
    # 检查是否包含冲突的忌事项
    has_bad_items = any(item in ji_items for item in required_items[:2])  # 只检查最重要的两个
    
    return has_good_items and not has_bad_items

if __name__ == "__main__":
    # 生成从今天开始的90天数据
    today = date.today()
    calendar_data = generate_calendar_data(today, 90)
    
    # 保存为JSON文件
    with open("calendar_seed_data.json", "w", encoding="utf-8") as f:
        json.dump(calendar_data, f, ensure_ascii=False, indent=2)
    
    print(f"生成了{len(calendar_data)}天的黄历数据")
    print(f"日期范围：{today} 到 {today + timedelta(days=89)}")