import requests
import os
from datetime import datetime
from lunar_python import Solar  # 需要 pip install lunar-python

APPID = os.getenv("WX_APPID")
APPSECRET = os.getenv("WX_APPSECRET")
OPENID = os.getenv("WX_OPENID")
TEMPLATE_ID = os.getenv("WX_TEMPLATE_ID")

# ===== 在这里改你的城市和星座 =====
CITY_LAT = 31.2989    # 苏州纬度
CITY_LON = 120.5853   # 苏州经度
ZODIAC_SIGN = "pisces"  # 你的星座英文：aries/taurus/gemini/cancer/leo/virgo/libra/scorpio/sagittarius/capricorn/aquarius/pisces
# ==================================


def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    res = requests.get(url).json()
    if "access_token" not in res:
        print("获取token失败：", res)
        raise Exception("token获取失败")
    return res["access_token"]


def get_weather():
    """从 Open-Meteo 获取实时天气 + 今日最高最低温"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={CITY_LAT}&longitude={CITY_LON}&current=temperature_2m,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=Asia/Shanghai"
    res = requests.get(url, timeout=10).json()

    weather_code_map = {
        0: "晴", 1: "晴间多云", 2: "多云", 3: "阴",
        45: "雾", 48: "雾凇", 51: "小毛毛雨", 53: "中毛毛雨", 55: "大毛毛雨",
        61: "小雨", 63: "中雨", 65: "大雨", 66: "冻雨", 67: "强冻雨",
        71: "小雪", 73: "中雪", 75: "大雪", 77: "阵雪",
        80: "小阵雨", 81: "中阵雨", 82: "强阵雨",
        95: "雷阵雨", 96: "雷阵雨伴冰雹", 99: "强雷阵雨伴冰雹"
    }

    current = res.get("current", {})
    daily = res.get("daily", {})

    temp_now = current.get("temperature_2m", "--")
    code = current.get("weather_code", 0)
    weather_text = weather_code_map.get(code, f"未知({code})")
    temp_max = daily.get("temperature_2m_max", ["--"])[0]
    temp_min = daily.get("temperature_2m_min", ["--"])[0]

    return f"{weather_text} {temp_now}°C（{temp_min}°~{temp_max}°）"


def get_horoscope():
    """从 aztro API 获取今日星座运势"""
    url = f"https://aztro.sameerkumar.website/?sign={ZODIAC_SIGN}&day=today"
    res = requests.post(url, timeout=10).json()

    mood = res.get("mood", "")
    lucky_color = res.get("color", "")
    lucky_num = res.get("lucky_number", "")
    description = res.get("description", "")

    # 截取前50字，避免太长
    short_desc = description[:50] + "..." if len(description) > 50 else description
    return f"{short_desc}\n运势心情：{mood} | 幸运色：{lucky_color} | 幸运数字：{lucky_num}"


def get_lunar():
    """用 lunar-python 库本地计算农历+宜忌"""
    today = Solar.fromDate(datetime.now())
    lunar = today.getLunar()

    lunar_date = f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
    animal = lunar.getYearShengXiao()  # 生肖
    ganzhi_year = lunar.getYearInGanZhi()  # 干支年
    yi = "、".join(lunar.getDayYi()[:3])  # 宜（取前3个）
    ji = "、".join(lunar.getDayJi()[:3])  # 忌（取前3个）

    return f"{ganzhi_year}年({animal}) {lunar_date}\n宜：{yi}\n忌：{ji}"


def send_msg():
    token = get_token()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    weather = get_weather()
    horo = get_horoscope()
    lunar = get_lunar()

    todo_list = """1. 完成今日工作复盘
2. 学习软考高项资料30分钟
3. 晚上健身30分钟"""

    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "time": {"value": now},
            "weather": {"value": weather},
            "horo": {"value": horo},
            "lunar": {"value": lunar},
            "todo": {"value": todo_list}
        }
    }
    resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}",
        json=data
    )
    print("微信返回：", resp.json())


if __name__ == "__main__":
    send_msg()
