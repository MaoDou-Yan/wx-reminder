import requests
import os
from datetime import datetime
import pytz
from lunar_python import Solar

# ===== 微信配置 =====
APPID = os.getenv("WX_APPID")
APPSECRET = os.getenv("WX_APPSECRET")
OPENID = os.getenv("WX_OPENID")
TEMPLATE_ID = os.getenv("WX_TEMPLATE_ID")

# ===== 聚合数据 =====
JUHE_WEATHER_KEY = os.getenv("JUHE_WEATHER_KEY")
JUHE_HORO_KEY = os.getenv("JUHE_HORO_KEY")

# ===== 固定参数 =====
CITY_NAME = "徐州"
CONS_NAME = "双鱼座"
TIMEZONE = pytz.timezone("Asia/Shanghai")
LINE_MAX = 20  # 每行最多20汉字


def split_text(text, max_len):
    """按字数切割文本，返回列表"""
    res = []
    if not text:
        return res
    for i in range(0, len(text), max_len):
        res.append(text[i:i+max_len])
    return res


def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    res = requests.get(url, timeout=10).json()
    if "access_token" not in res:
        print("获取token失败：", res)
        raise Exception("token获取失败")
    return res["access_token"]


def get_weather():
    try:
        url = "https://apis.juhe.cn/simpleWeather/query"
        params = {"key": JUHE_WEATHER_KEY, "city": CITY_NAME, "future_num": 1}
        res = requests.get(url, params=params, timeout=10).json()
        if res.get("error_code") != 0:
            return "获取失败"
        rt = res["result"]
        now = rt["realtime"]
        today = rt["future"][0]
        # 控制在20字以内
        return f"{now['info']} {now['temperature']}℃（{today['temperature']}）"
    except Exception as e:
        print("天气异常：", e)
        return "获取失败"


def get_horo():
    """返回 (头部行, 正文行列表)"""
    try:
        url = "http://web.juhe.cn/constellation/getAll"
        params = {"key": JUHE_HORO_KEY, "consName": CONS_NAME, "type": "today"}
        res = requests.get(url, params=params, timeout=10).json()
        if res.get("error_code") != 0:
            return "综合-- | -- | --", []

        all_score = res.get("all", "--")
        color = res.get("color", "--")
        number = res.get("number", "--")
        summary = res.get("summary", "")

        head = f"综合{all_score} | {color} | {number}"
        lines = split_text(summary, LINE_MAX)
        return head, lines

    except Exception as e:
        print("星座异常：", e)
        return "获取失败", []


def get_lunar_date():
    try:
        now = datetime.now(tz=TIMEZONE)
        lunar = Solar.fromDate(now).getLunar()
        ganzhi = lunar.getYearInGanZhi()
        animal = lunar.getYearShengXiao()
        month = lunar.getMonthInChinese()
        day = lunar.getDayInChinese()
        return f"{ganzhi}({animal}) {month}{day}"
    except Exception as e:
        print("农历日期异常：", e)
        return "获取失败"


def get_yiji():
    try:
        now = datetime.now(tz=TIMEZONE)
        lunar = Solar.fromDate(now).getLunar()
        yi = "、".join(lunar.getDayYi()[:2])
        ji = "、".join(lunar.getDayJi()[:2])
        return f"宜:{yi} 忌:{ji}"
    except Exception as e:
        print("宜忌异常：", e)
        return "获取失败"


def send_msg():
    token = get_token()
    now = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    weather = get_weather()
    horo_head, horo_lines = get_horo()
    lunar_date = get_lunar_date()
    yiji = get_yiji()

    todo = "1.工作复盘 2.软考学习\n3.健身30分钟"

    # 关键：空行统一填 "-"，微信就不会吞行
    line1 = horo_lines[0] if len(horo_lines) >= 1 else "-"
    line2 = horo_lines[1] if len(horo_lines) >= 2 else "-"
    line3 = horo_lines[2] if len(horo_lines) >= 3 else "-"
    line4 = horo_lines[3] if len(horo_lines) >= 4 else "-"

    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "time": {"value": now},
            "weather": {"value": weather},
            "horo_head": {"value": horo_head},
            "horo_line1": {"value": line1},
            "horo_line2": {"value": line2},
            "horo_line3": {"value": line3},
            "horo_line4": {"value": line4},
            "lunar_date": {"value": lunar_date},
            "yiji": {"value": yiji},
            "todo": {"value": todo}
        }
    }
    resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}",
        json=data,
        timeout=10
    )
    print("微信返回：", resp.json())


if __name__ == "__main__":
    send_msg()
