const { spawn } = require('child_process');
const path = require('path');

export default async function handler(req, res) {
  console.log('API endpoint hit');
  
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      const scriptPath = path.join(process.cwd(), 'scraper.py');
      
      const python = spawn('python3', [scriptPath]);
      
      let dataString = '';
      let errorString = '';

      python.stdout.on('data', (data) => {
        dataString += data.toString();
        console.log(`输出: ${data}`);
      });

      python.stderr.on('data', (data) => {
        errorString += data.toString();
        console.error(`错误: ${data}`);
      });

      python.on('close', (code) => {
        console.log(`子进程退出码：${code}`);
        res.status(200).json({
          status: code === 0 ? 'success' : 'error',
          output: dataString,
          error: errorString || null
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
