import requests
import os

APPID = os.getenv("WX_APPID")
APPSECRET = os.getenv("WX_APPSECRET")
OPENID = os.getenv("WX_OPENID")
TEMPLATE_ID = os.getenv("WX_TEMPLATE_ID")

def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    res = requests.get(url).json()
    return res["access_token"]

def send_msg(content):
    token = get_token()
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "notice": {"value": content}
        }
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    # 这里写你的提醒内容
    send_msg("【定时提醒】该做XX事情啦！")