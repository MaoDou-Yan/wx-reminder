import requests
import os
from datetime import datetime
from lunar_python import Solar

# ===== 微信配置（Secrets）=====
APPID = os.getenv("WX_APPID")
APPSECRET = os.getenv("WX_APPSECRET")
OPENID = os.getenv("WX_OPENID")
TEMPLATE_ID = os.getenv("WX_TEMPLATE_ID")

# ===== 聚合数据配置（Secrets）=====
# 同一个聚合账号下的天气+星座，通常共用一个key
JUHE_KEY = os.getenv("JUHE_KEY")

# ===== 固定参数 =====
CITY_NAME = "徐州"
CONS_NAME = "双鱼座"


def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    res = requests.get(url, timeout=10).json()
    if "access_token" not in res:
        print("获取token失败：", res)
        raise Exception("token获取失败")
    return res["access_token"]


def get_weather():
    """聚合数据 - 徐州实时天气 + 今日温度范围"""
    try:
        url = "https://apis.juhe.cn/simpleWeather/query"
        params = {
            "key": JUHE_KEY,
            "city": CITY_NAME,
            "future_num": 1
        }
        res = requests.get(url, params=params, timeout=10).json()

        if res.get("error_code") != 0:
            print("天气接口错误：", res.get("reason"))
            return "天气获取失败"

        result = res.get("result", {})
        realtime = result.get("realtime", {})
        future = result.get("future", [{}])[0]

        temp_now = realtime.get("temperature", "--")
        weather_info = realtime.get("info", "--")
        direct = realtime.get("direct", "")
        power = realtime.get("power", "")
        today_temp = future.get("temperature", "--")  # 格式如 "1/7℃"

        return f"{weather_info} {temp_now}°C（{today_temp}）\n{direct} {power}"

    except Exception as e:
        print("天气接口异常：", e)
        return "天气获取失败"


def get_horoscope():
    """聚合数据 - 双鱼座今日运势"""
    try:
        url = "http://web.juhe.cn/constellation/getAll"
        params = {
            "key": JUHE_KEY,
            "consName": CONS_NAME,
            "type": "today"
        }
        res = requests.get(url, params=params, timeout=10).json()

        if res.get("error_code") != 0:
            print("星座接口错误：", res.get("reason"))
            return "星座运势获取失败"

        all_score = res.get("all", "")
        color = res.get("color", "")
        number = res.get("number", "")
        summary = res.get("summary", "")

        # 截取前60字，避免模板消息超长
        short = summary[:60] + "..." if len(summary) > 60 else summary

        return f"{short}\n综合指数：{all_score} | 幸运色：{color} | 幸运数字：{number}"

    except Exception as e:
        print("星座接口异常：", e)
        return "星座运势获取失败"


def get_lunar():
    """本地计算 - 农历黄历（干支、生肖、宜、忌）"""
    try:
        now = datetime.now()
        solar = Solar.fromDate(now)
        lunar = solar.getLunar()

        lunar_date = f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
        ganzhi = lunar.getYearInGanZhi()
        animal = lunar.getYearShengXiao()
        yi = "、".join(lunar.getDayYi()[:3])
        ji = "、".join(lunar.getDayJi()[:3])

        return f"{ganzhi}年({animal}) {lunar_date}\n宜：{yi}\n忌：{ji}"

    except Exception as e:
        print("农历黄历异常：", e)
        return "农历黄历获取失败"


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
        json=data,
        timeout=10
    )
    print("微信返回：", resp.json())


if __name__ == "__main__":
    send_msg()
