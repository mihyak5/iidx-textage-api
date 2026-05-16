const axios = require('axios');
const iconv = require('iconv-lite');
const fs = require('fs');
const vm = require('vm');

// 把所有需要抓取的文件名列在数组里
const targetFiles = [
    "titletbl.js",
    "datatbl.js",
    "actbl.js",
    "cstbl.js",
    "cstbl1.js",
    "cstbl2.js",
    "cltbl.js",
    "stepup.js"
];

// 一个简单的延迟函数，用来做“礼貌抓取”
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchAllData() {
    console.log(`🚀 开始批量获取 Textage 数据，共 ${targetFiles.length} 个文件...\n`);

    for (const file of targetFiles) {
        const url = `http://textage.cc/score/${file}`;
        const baseName = file.replace('.js', ''); // 例如 titletbl
        const jsonFileName = `${baseName}.json`;

        try {
            console.log(`⏳ 正在请求: ${file} ...`);
            const response = await axios.get(url, {
                responseType: 'arraybuffer',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'http://textage.cc/'
                },
                timeout: 30000 
            });

            // 完美解码日文
            const jsCode = iconv.decode(response.data, 'cp932');
            
            // 为每个文件创建一个干净、独立的 V8 虚拟机环境
            const sandbox = {};
            vm.createContext(sandbox);
            
            // 执行站长代码
            vm.runInContext(jsCode, sandbox);

            // 【智能提取机制】
            // 站长的 JS 通常会定义一个和文件名同名的全局变量（比如 datatbl.js 定义了 datatbl）
            // 也有可能定义了多个辅助变量。我们优先提取同名变量；如果没有，就把整个运行结果保存下来。
            let dataToSave = sandbox[baseName] ? sandbox[baseName] : sandbox;

            // 保存为标准的 JSON 文件
            fs.writeFileSync(jsonFileName, JSON.stringify(dataToSave, null, 2));
            
            console.log(`✅ 成功清洗并保存为 -> ${jsonFileName}`);

        } catch (error) {
            console.error(`❌ 获取或解析 ${file} 失败:`, error.message);
        }

        // 礼貌性暂停 2 秒，防止被站长服务器封禁 IP
        await sleep(2000);
    }
    
    console.log("\n🎉 所有数据处理完毕！");
}

fetchAllData();
