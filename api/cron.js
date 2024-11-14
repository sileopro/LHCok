const { exec } = require('child_process');

export default async function handler(req, res) {
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      
      exec('python scraper.py', (error, stdout, stderr) => {
        if (error) {
          console.error(`执行错误: ${error}`);
          return res.status(500).json({ error: error.message });
        }
        
        console.log(`标准输出: ${stdout}`);
        if (stderr) {
          console.error(`标准错误: ${stderr}`);
        }
        
        // 尝试读取结果文件
        const results = {};
        ['lam', 'xam', 'hk', 'tc'].forEach(type => {
          try {
            const result = require('fs').readFileSync(`${type}.txt`, 'utf8');
            results[type] = result;
          } catch (e) {
            console.error(`读取${type}.txt失败:`, e);
            results[type] = null;
          }
        });
        
        res.status(200).json({ 
          message: '执行成功', 
          output: stdout,
          results: results 
        });
      });
    } catch (error) {
      console.error('执行过程中出错:', error);
      res.status(500).json({ error: error.message });
    }
  } else {
    res.status(405).json({ error: '方法不允许' });
  }
} 