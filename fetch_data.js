const axios = require('axios');
const iconv = require('iconv-lite');
const fs = require('fs');
const vm = require('vm'); // Node.js 内置的虚拟机模块，专门用来安全运行 JS 字符串

async function fetchAndCleanData() {
    console.log("开始获取 textage 数据 (Node.js V8 引擎版)...");
    const url = "http://textage.cc/score/titletbl.js";

    try {
        // 请求数据，注意这里必须用 arraybuffer 接收原始字节，防止乱码
        const response = await axios.get(url, {
            responseType: 'arraybuffer',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Referer': 'http://textage.cc/'
            },
            timeout: 30000 // 30秒超时
        });

        // 完美解码日文 Shift-JIS / CP932
        const jsCode = iconv.decode(response.data, 'cp932');
        console.log(`成功获取代码，长度: ${jsCode.length}`);

        // 【最核心的黑科技】：创建一个虚拟的浏览器环境 (Context)
        const sandbox = {};
        vm.createContext(sandbox);

        // 让 V8 引擎直接运行站长的代码！
        // V8 引擎会自动处理所有的 /* */ 注释、错乱的引号、奇怪的变量
        vm.runInContext(jsCode, sandbox);

        // 运行完毕后，站长的 titletbl 数据就已经完美存在于 sandbox 中了！
        if (sandbox.titletbl) {
            fs.writeFileSync('titletbl.json', JSON.stringify(sandbox.titletbl, null, 2));
            console.log(`🎉 绝杀！V8 引擎完美解析，保存了 ${Object.keys(sandbox.titletbl).length} 首曲目数据！`);
        } else {
            console.log("❌ 未能在代码中找到 titletbl 变量。");
        }

    } catch (error) {
        console.error("❌ 发生错误：", error.message);
    }
}

fetchAndCleanData();
