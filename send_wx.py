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

def send_msg():
    token = get_token()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "touser": OPENID,
        "template_id": TEMPLATE_ID,
        "data": {
            "time": {"value": now},
            "weather": {"value": "晴，22~30℃"},
            "horo": {"value": "今日运势平稳"},
            "lunar": {"value": "丙午年九月廿二"},
            "todo": {"value": "1. 完成测试\n2. 整理文档"}
        }
    }
    resp = requests.post(f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}", json=data)
    print("微信返回：", resp.json())

if __name__ == "__main__":
    send_msg()
