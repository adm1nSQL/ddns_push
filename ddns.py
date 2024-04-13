import requests
import json
# import schedule
# import time

bot_token = '你的tg机器人token'
chat_id = '需要推送通知的群或个人ID'
cf_account = '你的cloudflare账号'
api_key = '你的cloudflare账号的api密钥'
zone_id = 'cloudflare中需要使用脚本的域名zone_id'
sub_domain = '需要使用脚本的域名或子域名，例如 a.example.com'


def send_message(text):
    message_data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'MarkdownV2'
    }
    print(text)
    try:
        res = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=message_data)
        if res.status_code == 200:
            print("发送成功")
            res.close()
        else:
            print("发送失败")
    except Exception as e:
        print(e)


def update_dns_ip(new_ip):
    headers = {
        "X-Auth-Email": cf_account,
        "X-Auth-Key": api_key,
    }

    index_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={sub_domain}"
    response = requests.get(index_url, headers=headers)
    record_id = response.json()["result"][0]["id"]

    update_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    payload = {
        "content": new_ip
    }
    headers["Content-Type"] = "application/json"
    update_response = requests.patch(update_url, headers=headers, data=json.dumps(payload))
    print(update_response.json())
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            raw_msg = "✅优选IP更新成功！"
            send_message(raw_msg)
        else:
            print(update_response.json())
            raw_msg = f"❌优选IP更新失败，状态码：{update_response.status_code}"
            send_message(raw_msg)
    else:
        raw_msg = f"❌优选IP更新失败，状态码：{update_response.status_code}"
        send_message(raw_msg)


def get_current_ip():
    api1 = "https://monitor.gacjie.cn/api/client/get_ip_address"
    api2 = "https://cfnode.eu.org/api/ajax/get_opt_v4"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/108.0.0.0 '
                      'Safari/537.36'}

    response = requests.get(url=api1, headers=headers, timeout=15).json()
    try:
        if response['msg'] == "查询成功":
            ip_list = response['info']['CM']
            ip_list1 = response['info']['CU']
            ip_list2 = response['info']['CT']
            lists = ip_list + ip_list1 + ip_list2
            max_item = max(lists, key=lambda x: x['bandwidth'])
            # 提取对应的字段
            max_address = max_item['address']
            max_bandwidth = max_item['bandwidth']
            max_bandwidth = str(max_bandwidth) + "MB"
            max_delay = max_item['delay']
            max_colo = max_item['colo']
            max_device_name = max_item['line_name']

            text = f"✅*本次优选IP获取成功*\n*仅网页加速，不可用于节点*\nCName域名： `{sub_domain}`\n当前源：`Default`\n更新频率：`4H`\n\n最优IP：`{max_address}`\n速度：`{max_bandwidth}/S`\n延迟：`{max_delay} ms`\n数据中心：`{max_colo}`\n测速服务器：`{max_device_name}`\n\n开始尝试切换DNS解析……"
            send_message(text)

            update_dns_ip(max_address)

        else:
            res = requests.get(url=api2, headers=headers, timeout=15).json()
            if res['msg'] == "查询成功":
                ip_list = res['data']
                max_item = max(ip_list, key=lambda x: x['bandwidth'])
                # 提取对应的字段
                max_address = max_item['address']
                max_bandwidth = max_item['bandwidth']
                max_delay = max_item['delay']
                max_colo = max_item['colo']
                max_device_name = max_item['device_name']

                text = f"✅*本次优选IP获取成功*\n*仅网页加速，不可用于节点*\nCName域名： `{sub_domain}`\n当前源：`Second`\n更新频率：`4H`\n\n最优IP：`{max_address}`\n速度：`{max_bandwidth}/S`\n延迟：`{max_delay} ms`\n数据中心：`{max_colo}`\n测速服务器：`{max_device_name}`\n\n开始尝试切换DNS解析……"
                send_message(text)

                update_dns_ip(max_address)

    except Exception as e:
        notice = response['msg'] if response['msg'] else "API出现问题，请检查！"
        text = "❌*本次优选IP获取失败*\n\n故障原因：" + notice + str(e)
        send_message(text)


# def job():
#     get_current_ip()
#
#
# schedule.every(4).hours.do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

if __name__ == '__main__':
    get_current_ip()
