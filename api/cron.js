const { exec } = require('child_process');
const path = require('path');

export default async function handler(req, res) {
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      const scriptPath = path.join(process.cwd(), 'scraper.py');
      const pythonPath = process.env.PYTHON_PATH || '/usr/local/bin/python3';
      
      console.log(`使用 Python 路径: ${pythonPath}`);
      console.log(`脚本路径: ${scriptPath}`);
      
      exec(`${pythonPath} ${scriptPath}`, (error, stdout, stderr) => {
        if (error) {
          console.error(`执行错误: ${error}`);
          return res.status(500).json({ 
            error: error.message,
            details: stderr,
            pythonPath: pythonPath,
            scriptPath: scriptPath
          });
        }
        
        console.log(`输出: ${stdout}`);
        res.status(200).json({ 
          status: 'success',
          output: stdout,
          error: stderr || null
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
