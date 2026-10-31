import requests
import os

APPID = os.getenv("wx88c4b9aa2bf1498b")
APPSECRET = os.getenv("d85d39a90adb9ef956a7028a59198c5a")
OPENID = os.getenv("oxXJw3HRx1rXBMeTQ7Gupiuba-ro")
TEMPLATE_ID = os.getenv("7fU6M7bSdpDq4d261_7PSGakMQuo6W_u4Smf-6sImpU")

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