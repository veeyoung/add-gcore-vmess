import os, sys, json, base64, datetime
import requests


def log(msg):
    time = datetime.datetime.now()
    print('[' + time.strftime('%Y.%m.%d-%H:%M:%S') + '] ' + msg)


# 保存到文件
def save_to_file(file_name, content):
    with open(file_name, 'w') as f:
        for line in content:
            f.write(line + '\n')


# 获取cdn数据:
def get_cdn_ip(cdns, local_cdns):
    if cdns is None or cdns == '':
        sys.exit()
    try:
        gcore_cdns = requests.get(cdns, timeout=5).text
    except Exception as r:
        log('网络GcoreCdn加载失败:{},尝试本地文件'.format(r))
        try:
            f = open(local_cdns, 'r', encoding="utf-8")
            gcore_cdns = f.read()
            f.close()
        except :
            log('本地cdn列表加载失败')
            sys.exit()
    all_cdn = json.loads(gcore_cdns)
    ipv4_cdn = all_cdn.get('addresses')
    return ipv4_cdn


# 解密vmess节点
def decode_v2ray_node(node):
    decode_proxy = node[8:]
    if not decode_proxy or decode_proxy.isspace():
        log('vmess节点信息为空')
    proxy_str = base64.b64decode(decode_proxy).decode('utf-8')
    proxy_res = json.loads(proxy_str)
    return proxy_res


# 还原vmess节点
def encode_v2ray_node(node):
    proxy_str = json.dumps(node)
    encode_proxy = base64.b64encode(proxy_str.encode('utf-8')).decode('utf-8')
    proxy_res = 'vmess://' + str(encode_proxy)
    return proxy_res


# 把cdn添加到vmess节点:
def add_to_vmess(cdn_list, vmess):
    barevmess = decode_v2ray_node(vmess)
    name = barevmess['ps']
    proxy_list = []
    for ip in cdn_list:
        ip = ip[:ip.find('/')]
        barevmess['ps'] = name + ip
        barevmess['add'] = ip
        res_vmess = encode_v2ray_node(barevmess)
        proxy_list.append(res_vmess)

    return proxy_list

# 程序入口
if __name__ == '__main__':
    input_vmess = input('请输入vmess节点')
    output_vmesses = 'gcore-vmesses.txt'
    gcore_cdn_ips = 'https://api.gcore.com/cdn/public-ip-list'
    local_cdn = 'public-ip-list.json'
    cdn_ip_list = get_cdn_ip(gcore_cdn_ips, local_cdn)
    result_vmesses = add_to_vmess(cdn_ip_list, input_vmess)
    save_to_file(output_vmesses, result_vmesses)
    print(f'节点已导出至 {output_vmesses}')
