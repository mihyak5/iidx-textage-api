const axios = require('axios');
const iconv = require('iconv-lite');
const fs = require('fs');
const vm = require('vm');

// 【映射表】：文件名 -> 对应的内部变量名
const targetFiles = [
    { file: "titletbl.js", varName: "titletbl" },
    { file: "datatbl.js", varName: "datatbl" },
    { file: "actbl.js", varName: "actbl" },
    
    // 家用机和段位认定表，它们都是不断往 cstbl 这个大数组里追加数据
    { file: "cstbl.js", varName: "cstbl" },
    { file: "cstbl1.js", varName: "cstbl" },
    { file: "cstbl2.js", varName: "cstbl" },
    { file: "cltbl.js", varName: "cstbl" }, 
    
    // Step Up 模式的变量名叫 su_list
    { file: "stepup.js", varName: "su_list" }
];

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchAllData() {
    console.log(`🚀 开始批量获取 Textage 数据...\n`);

    // 【核心修复 1】：创建一个全局共享沙箱，模拟一个持续打开的浏览器标签页
    const sandbox = {
        // 【核心修复 2】：预先注入站长省略了引号的十六进制常数 (代表难度等级 10~15)
        A: 10, B: 11, C: 12, D: 13, E: 14, F: 15,
        cstbl: new Array() // 提前建好数组兜底，防止意外
    };
    vm.createContext(sandbox);

    for (const target of targetFiles) {
        const url = `http://textage.cc/score/${target.file}`;
        const jsonFileName = target.file.replace('.js', '.json');

        try {
            console.log(`⏳ 正在请求: ${target.file} ...`);
            const response = await axios.get(url, {
                responseType: 'arraybuffer',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Referer': 'http://textage.cc/'
                },
                timeout: 30000 
            });

            // 完美解码日文
            const jsCode = iconv.decode(response.data, 'cp932');
            
            // 在【同一个沙箱】中执行所有代码！这样变量就会跨文件累加
            vm.runInContext(jsCode, sandbox);

            // 提取出对应的对象
            const dataToSave = sandbox[target.varName];

            if (dataToSave) {
                // 保存为标准的 JSON 文件
                fs.writeFileSync(jsonFileName, JSON.stringify(dataToSave, null, 2));
                console.log(`✅ 成功清洗并保存为 -> ${jsonFileName}`);
            } else {
                console.log(`⚠️ 运行成功，但未能找到变量 ${target.varName}`);
            }

        } catch (error) {
            console.error(`❌ 获取或解析 ${target.file} 失败:`, error.message);
        }

        // 礼貌性暂停 2 秒
        await sleep(2000);
    }
    
    console.log("\n🎉 所有数据处理完毕！");
}

fetchAllData();
