import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import re
import traceback
import ast

def fetch_and_clean_data():
    print("开始获取 textage 数据...")
    url = "http://textage.cc/score/titletbl.js"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://textage.cc/'
    }
    
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=2)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        response = session.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print("❌ 请求失败！")
            return

        response.encoding = 'cp932'
        js_text = response.text
        
        # 【终极防御 1】：无情抹除文件里潜藏的所有不可见“幽灵”控制字符（仅保留换行和回车）
        js_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', js_text)

        match = re.search(r'titletbl\s*=\s*(\{.*?\})\s*;', js_text, re.DOTALL)
        
        if match:
            raw_js_object = match.group(1)
            
            # 【终极防御 2】：放弃 chompjs，把站长的 JS 对象当成 Python 字典来强行解析
            safe_str = raw_js_object
            safe_str = re.sub(r'//.*', '', safe_str) # 删掉 JS 的单行注释
            
            # 将 JS 独有的 null 等小写关键字替换为 Python 认识的大写关键字
            safe_str = re.sub(r'\btrue\b', 'True', safe_str)
            safe_str = re.sub(r'\bfalse\b', 'False', safe_str)
            safe_str = re.sub(r'\bnull\b', 'None', safe_str)
            safe_str = re.sub(r'\bundefined\b', 'None', safe_str)

            try:
                # ast.literal_eval 是 Python 内置的绝对安全的字符串转字典神器
                clean_data = ast.literal_eval(safe_str)
                
                with open("titletbl.json", "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, ensure_ascii=False, indent=2)
                    
                print(f"🎉 成功绝杀！完美越过所有语法陷阱，清洗并保存了 {len(clean_data)} 条曲目数据！")
                
            except SyntaxError as se:
                print(f"❌ 解析依然失败！Python 精确指出了语法错误在第 {se.lineno} 行：")
                print(se.text)
                if se.offset:
                    print(" " * (se.offset - 1) + "^ <--- 罪魁祸首在这里")
        else:
            print("❌ 未找到目标数据对象！")
            
    except Exception as e:
        print("❌ 发生系统级报错：")
        traceback.print_exc()

if __name__ == "__main__":
    fetch_and_clean_data()
