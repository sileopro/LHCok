const puppeteer = require('puppeteer');

async function scrape() {
    const browser = await puppeteer.launch({
        headless: "new",
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920x1080'
        ]
    });
    
    try {
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
        
        console.log('正在访问页面...');
        await page.goto('https://akjw09d.48489aaa.com:8800/', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });
        
        console.log('等待页面加载...');
        await page.waitForTimeout(5000);
        
        const results = {};
        const lotteryTypes = {
            'lam': ['AMLHC2', '老澳门六合彩'],
            'xam': ['AMLHC3', '新澳门六合彩'],
            'hk': ['LHC', '六合彩'],
            'tc': ['TWLHC', '台湾六合彩']
        };
        
        for (const [id, [code, name]] of Object.entries(lotteryTypes)) {
            try {
                console.log(`处理 ${name}...`);
                const lotteryDiv = await page.$(`#${code}`);
                if (!lotteryDiv) {
                    console.log(`未找到 ${name} 区块`);
                    continue;
                }
                
                const issueElement = await lotteryDiv.$('.preDrawIssue');
                if (!issueElement) continue;
                
                const issueText = await page.evaluate(el => el.textContent, issueElement);
                const issueMatch = issueText.match(/(\d+)$/);
                if (!issueMatch) continue;
                
                const issueShort = issueMatch[1].slice(-3);
                
                const numbers = [];
                let specialNumber = null;
                let specialZodiac = null;
                
                const numberElements = await lotteryDiv.$$('li:not(.xgcaddF1)');
                
                for (let i = 0; i < numberElements.length; i++) {
                    const elem = numberElements[i];
                    const number = await elem.$eval('span', el => el.textContent.padStart(2, '0'));
                    const zodiac = await elem.$eval('.animal', el => el.textContent);
                    
                    if (i === numberElements.length - 1) {
                        specialNumber = number;
                        specialZodiac = zodiac;
                    } else {
                        numbers.push(number);
                    }
                }
                
                if (numbers.length && specialNumber) {
                    results[id] = `第${issueShort}期：${numbers.join(' ')} 特码 ${specialNumber} ${specialZodiac}`;
                    console.log(`成功获取 ${name} 结果`);
                }
            } catch (error) {
                console.error(`处理 ${name} 时出错:`, error);
            }
        }
        
        console.log('完成数据获取');
        console.log(JSON.stringify(results));
        
    } finally {
        await browser.close();
    }
}

scrape().catch(error => {
    console.error('执行出错:', error);
    process.exit(1);
}); 