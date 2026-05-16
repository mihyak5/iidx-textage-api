import requests
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
    
    try:
        print(f"正在请求 {url} ...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败！")
            return

        response.encoding = 'shift_jis'
        js_text = response.text
        
        print(f"成功获取到文件，文件总长度: {len(js_text)} 字符")

        # 【核心修复】：将正则里的 \[ \] 改成了 \{ \}，并使用贪婪匹配 .* 抓取整个对象
        match = re.search(r'titletbl\s*=\s*(\{.*\})', js_text, re.DOTALL)
        
        if match:
            raw_js_object = match.group(1)
            print(f"成功定位到数据对象！")
            
            try:
                # chompjs 会完美把非标准的 JS 对象转成 Python 字典
                clean_data = chompjs.parse_js_object(raw_js_object)
                
                with open("titletbl.json", "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)
                    
                print(f"🎉 大成功！清洗并保存了 {len(clean_data)} 条曲目数据！")
            except Exception as parse_error:
                print(f"❌ JSON 解析失败！")
                print(f"详细错误: {parse_error}")
        else:
            print("❌ 未找到目标数据对象！")
            print(f"我们抓取到的文件开头是长这样的: {js_text[:300]}")
            
    except Exception as e:
        print("❌ 发生致命网络/系统错误：")
        traceback.print_exc()

if __name__ == "__main__":
    fetch_and_clean_data()
