import requests
import os
from datetime import datetime
import pytz
from lunar_python import Solar

# ========== 配置区 ==========
APPID = os.getenv("WX_APPID")
APPSECRET = os.getenv("WX_APPSECRET")
OPENID = os.getenv("WX_OPENID")
TEMPLATE_ID = os.getenv("WX_TEMPLATE_ID")

JUHE_WEATHER_KEY = os.getenv("JUHE_WEATHER_KEY")
JUHE_HORO_KEY = os.getenv("JUHE_HORO_KEY")

CITY_NAME = "徐州"
CONS_NAME = "双鱼座"
TIMEZONE = pytz.timezone("Asia/Shanghai")
LINE_MAX = 17        # 星座摘要单行上限
PLACEHOLDER = "　"    # 全角空格占位，空行填充
# 代办清单，在这里修改内容
TODO_LIST = [
    "1.工作复盘",
    "2.软考学习",
    "3.健身30分钟",
    "",
    "",
    ""
]
# ===========================

def split_text(text, max_len):
    """按长度分割文本，用于星座summary"""
    res = []
    if not text:
        return res
    for i in range(0, len(text), max_len):
        res.append(text[i:i+max_len])
    return res

def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    ret = requests.get(url, timeout=10).json()
    if "access_token" not in ret:
        print("【错误】获取access_token失败：", ret)
        raise Exception("token获取失败")
    return ret["access_token"]

def get_weather():
    try:
        url = "https://apis.juhe.cn/simpleWeather/query"
        params = {"key": JUHE_WEATHER_KEY, "city": CITY_NAME, "future_num": 1}
        r = requests.get(url, params=params, timeout=10).json()
        if r.get("error_code") != 0:
            return "获取失败"
        rt = r["result"]
        now = rt["realtime"]
        today = rt["future"][0]
        return f"{now['info']} {now['temperature']}℃（{today['temperature']}）"
    except Exception as e:
        print("【异常】天气接口：", e)
        return "获取失败"

def get_horo_data():
    try:
        url = "http://web.juhe.cn/constellation/getAll"
        params = {"key": JUHE_HORO_KEY, "consName": CONS_NAME, "type": "today"}
        r = requests.get(url, params=params, timeout=10).json()
        if r.get("error_code") != 0:
            return {
                "name": CONS_NAME,
                "all": "--",
                "color": "--",
                "health": "--",
                "love": "--",
                "money": "--",
                "number": "--",
                "work": "--",
                "QFriend": "--",
                "summary": ""
            }
        return {
            "name": r.get("name", CONS_NAME),
            "all": r.get("all", "--"),
            "color": r.get("color", "--"),
            "health": r.get("health", "--"),
            "love": r.get("love", "--"),
            "money": r.get("money", "--"),
            "number": str(r.get("number", "--")),
            "work": r.get("work", "--"),
            "QFriend": r.get("QFriend", "--"),
            "summary": r.get("summary", "")
        }
    except Exception as e:
        print("【异常】星座接口：", e)
        return {
            "name": CONS_NAME,
            "all": "--",
            "color": "--",
            "health": "--",
            "love": "--",
            "money": "--",
            "number": "--",
            "work": "--",
            "QFriend": "--",
            "summary": ""
        }

def get_lunar_date():
    try:
        now = datetime.now(tz=TIMEZONE)
        lunar = Solar.fromDate(now).getLunar()
        gz = lunar.getYearInGanZhi()
        sx = lunar.getYearShengXiao()
        m = lunar.getMonthInChinese()
        d = lunar.getDayInChinese()
        return f"{gz}({sx}) {m}{d}"
    except Exception as e:
        print("【异常】农历：", e)
        return "获取失败"

def get_yiji():
    try:
        now = datetime.now(tz=TIMEZONE)
        lunar = Solar.fromDate(now).getLunar()
        yi = "、".join(lunar.getDayYi()[:2])
        ji = "、".join(lunar.getDayJi()[:2])
        return f"宜:{yi} 忌:{ji}"
    except Exception as e:
        print("【异常】宜忌：", e)
        return "获取失败"

def fill_6_lines(src_list, placeholder):
    """统一补到6条，不足填充占位符"""
    out = []
    for i in range(6):
        if i < len(src_list) and src_list[i].strip() != "":
            out.append(src_list[i])
        else:
            out.append(placeholder)
    return out

def send_msg():
    token = get_token()
    now_str = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    weather = get_weather()
    horo = get_horo_data()
    lunar_date = get_lunar_date()
    yiji = get_yiji()

    # 拆分星座摘要 6行
    summary_parts = split_text(horo["summary"], LINE_MAX)
    horo_lines = fill_6_lines(summary_parts, PLACEHOLDER)

    # 代办填充到6行
    todo_lines = fill_6_lines(TODO_LIST, PLACEHOLDER)

    data_payload = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "time": {"value": now_str},
            "weather": {"value": weather},
            "cons_name": {"value": horo["name"]},
            "all": {"value": horo["all"]},
            "color": {"value": horo["color"]},
            "number": {"value": horo["number"]},
            "health": {"value": horo["health"]},
            "love": {"value": horo["love"]},
            "money": {"value": horo["money"]},
            "work": {"value": horo["work"]},
            "qfriend": {"value": horo["QFriend"]},
            "horo_line1": {"value": horo_lines[0]},
            "horo_line2": {"value": horo_lines[1]},
            "horo_line3": {"value": horo_lines[2]},
            "horo_line4": {"value": horo_lines[3]},
            "horo_line5": {"value": horo_lines[4]},
            "horo_line6": {"value": horo_lines[5]},
            "lunar_date": {"value": lunar_date},
            "yiji": {"value": yiji},
            "todo0": {"value": todo_lines[0]},
            "todo1": {"value": todo_lines[1]},
            "todo2": {"value": todo_lines[2]},
            "todo3": {"value": todo_lines[3]},
            "todo4": {"value": todo_lines[4]},
            "todo5": {"value": todo_lines[5]},
        }
    }
    print("===== 待发送data =====", data_payload)
    resp = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}",
        json=data_payload,
        timeout=10
    )
    print("===== 微信返回 =====", resp.json())

if __name__ == "__main__":
    send_msg()
