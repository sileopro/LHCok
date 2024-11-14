const { exec } = require('child_process');
const path = require('path');

export default async function handler(req, res) {
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      const scriptPath = path.join(process.cwd(), 'scraper.py');
      
      // 使用 which 命令找到 python3 的路径
      exec('which python3', (error, stdout, stderr) => {
        if (error) {
          console.error('找不到 python3:', error);
          return res.status(500).json({ error: 'Python3 not found' });
        }
        
        const pythonPath = stdout.trim();
        console.log('找到 Python 路径:', pythonPath);
        
        // 使用找到的 python3 路径执行脚本
        exec(`${pythonPath} ${scriptPath}`, (error, stdout, stderr) => {
          if (error) {
            console.error(`执行错误: ${error}`);
            return res.status(500).json({ 
              error: error.message,
              details: stderr
            });
          }
          
          console.log(`输出: ${stdout}`);
          res.status(200).json({ 
            status: 'success',
            output: stdout,
            error: stderr || null
          });
        });
      });
      
    } catch (error) {
      console.error('执行过程中出错:', error);
      res.status(500).json({ 
        error: error.message,
        stack: error.stack 
      });
    }
  } else {
    res.status(405).json({ error: '方法不允许' });
  }
} 
