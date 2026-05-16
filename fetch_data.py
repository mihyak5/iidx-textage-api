import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import chompjs
import json
import re
import traceback

def fetch_and_clean_data():
    print("开始获取 textage 数据...")
    url = "http://textage.cc/score/titletbl.js"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
        'Referer': 'http://textage.cc/'
    }
    
    # 【核心修复 1】：配置高级请求会话，加入自动重试机制
    session = requests.Session()
    retry_strategy = Retry(
        total=3,             # 最多重试 3 次
        backoff_factor=2,    # 每次重试的间隔时间递增 (0s, 2s, 4s)
        status_forcelist=[403, 429, 500, 502, 503, 504], # 遇到这些服务器错误也自动重试
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        print(f"正在请求 {url} ...")
        # 【核心修复 2】：使用 session 请求，并将超时时间从 15 秒放宽到 30 秒
        response = session.get(url, headers=headers, timeout=30)
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败！")
            return

        response.encoding = 'cp932'
        js_text = response.text
        
        print(f"成功获取到文件，文件总长度: {len(js_text)} 字符")

        match = re.search(r'titletbl\s*=\s*(\{.*?\})\s*;', js_text, re.DOTALL)
        
        if match:
            raw_js_object = match.group(1)
            print(f"成功定位到数据对象，有效代码长度: {len(raw_js_object)} 字符")
            
            vars_match = re.findall(r'^([A-Z0-9_]+)\s*=\s*([0-9]+);', js_text, re.MULTILINE)
            for var_name, var_value in vars_match:
                raw_js_object = re.sub(r'\b' + var_name + r'\b', var_value, raw_js_object)

            try:
                clean_data = chompjs.parse_js_object(raw_js_object)
                
                with open("titletbl.json", "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)
                    
                print(f"🎉 大成功！清洗并保存了 {len(clean_data)} 条曲目数据！")
                
            except Exception as parse_error:
                print(f"❌ JSON 解析失败！")
                err_str = str(parse_error)
                print(f"详细错误: {err_str}")
                
                err_match = re.search(r'char (\d+)', err_str)
                if err_match:
                    pos = int(err_match.group(1))
                    start = max(0, pos - 50)
                    end = min(len(raw_js_object), pos + 50)
                    print(f"\n⚠️ 解析崩溃位置附近的文本 (前后50字符):")
                    print("="*60)
                    print(raw_js_object[start:end])
                    print("="*60)
                    print(" " * (pos - start) + "^ <--- 就在这个字符附近发生了语法损坏")
        else:
            print("❌ 未找到目标数据对象！请检查正则。")
            
    except requests.exceptions.Timeout:
        print("❌ 网络超时！已经重试了 3 次，但服务器依然没有响应。这通常是源网站暂时无法访问，请稍后再跑一次 Actions。")
    except Exception as e:
        print("❌ 发生致命网络/系统错误：")
        traceback.print_exc()

if __name__ == "__main__":
    fetch_and_clean_data()
