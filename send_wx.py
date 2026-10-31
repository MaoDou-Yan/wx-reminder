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

def split_text_by_len(text, max_len):
    """按字数分割文本，返回列表，每段不超过max_len，空则返回空字符串"""
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
        params = {
            "key": JUHE_WEATHER_KEY,
            "city": CITY_NAME,
            "future_num": 1
        }
        res = requests.get(url, params=params, timeout=10).json()
        if res.get("error_code") != 0:
            print("天气接口错误：", res.get("reason"))
            return "获取失败"
        result = res.get("result", {})
        realtime = result.get("realtime", {})
        future = result.get("future", [{}])[0]
        temp_now = realtime.get("temperature", "--")
        weather_info = realtime.get("info", "--")
        today_temp = future.get("temperature", "--")
        return f"{weather_info} {temp_now}℃（{today_temp}）"
    except Exception as e:
        print("天气接口异常：", e)
        return "获取失败"

def get_horo_data():
    """只请求一次星座接口，返回原始数据，不截断"""
    try:
        url = "http://web.juhe.cn/constellation/getAll"
        params = {
            "key": JUHE_HORO_KEY,
            "consName": CONS_NAME,
            "type": "today"
        }
        res = requests.get(url, params=params, timeout=10).json()
        if res.get("error_code") != 0:
            print("星座接口错误：", res.get("reason"))
            return {"all":"--","color":"--","number":"--","summary":""}
        return {
            "all": res.get("all", "--"),
            "color": res.get("color", "--"),
            "number": res.get("number", "--"),
            "summary": res.get("summary", "")
        }
    except Exception as e:
        print("星座接口异常：", e)
        return {"all":"--","color":"--","number":"--","summary":""}

def get_lunar_date():
    try:
        now = datetime.now(tz=TIMEZONE)
        lunar = Solar.fromDate(now).getLunar()
        ganzhi = lunar.getYearInGanZhi()
        animal = lunar.getYearInGanZhi()
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
    horo = get_horo_data()
    horo_head = f"综合{horo['all']} | {horo['color']} | {horo['number']}"
    line_list = split_text_by_len(horo["summary"], LINE_MAX)

    # 预先填充4行，不足的自动为空字符串
    horo_line1 = line_list[0] if len(line_list)>=1 else ""
    horo_line2 = line_list[1] if len(line_list)>=2 else ""
    horo_line3 = line_list[2] if len(line_list)>=3 else ""
    horo_line4 = line_list[3] if len(line_list)>=4 else ""

    lunar_date = get_lunar_date()
    yiji = get_yiji()
    todo_list = "1.完成今日工作复盘\n2.学习软考高项资料30分钟\n3.晚上健身30分钟"

    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "time": {"value": now},
            "weather": {"value": weather},
            "horo_head": {"value": horo_head},
            "horo_line1": {"value": horo_line1},
            "horo_line2": {"value": horo_line2},
            "horo_line3": {"value": horo_line3},
            "horo_line4": {"value": horo_line4},
            "lunar_date": {"value": lunar_date},
            "yiji": {"value": yiji},
            "todo": {"value": todo_list}
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
