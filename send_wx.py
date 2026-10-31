import requests
import os
from datetime import datetime

APPID = os.getenv("WX_APPID")
APPSECRET = os.getenv("WX_APPSECRET")
OPENID = os.getenv("WX_OPENID")
TEMPLATE_ID = os.getenv("WX_TEMPLATE_ID")

def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    res = requests.get(url).json()
    if "access_token" not in res:
        print("获取token失败：", res)
        raise Exception("token获取失败")
    return res["access_token"]

def send_msg(content):
    token = get_token()
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    resp = requests.post(url, json={
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "notice": {"value": content}
        }
    })
    print("微信返回结果：", resp.json())

if __name__ == "__main__":
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # ========== 在这里修改你的内容 ==========
    msg = f"""{now}
——————————
🌤 【天气】


✨ 【星座运势】


📜 【农历运势】


📋 【今日代办】
1. xxxxx
2. xxxxx
"""
    send_msg(msg)
