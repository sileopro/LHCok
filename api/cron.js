const { exec } = require('child_process');
const path = require('path');

export default async function handler(req, res) {
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      const scriptPath = path.join(process.cwd(), 'scraper.py');
      
      // 尝试多个可能的 Python 路径
      const pythonCommands = [
        'python3',
        'python',
        '/opt/python/bin/python3',
        '/usr/bin/python3',
        'python3.9'
      ];

      let executed = false;
      
      for (const cmd of pythonCommands) {
        try {
          console.log(`尝试使用命令: ${cmd}`);
          exec(`${cmd} ${scriptPath}`, (error, stdout, stderr) => {
            if (!executed) {
              if (error) {
                console.error(`使用 ${cmd} 失败:`, error);
                return;
              }
              executed = true;
              console.log(`使用 ${cmd} 成功`);
              res.status(200).json({ 
                status: 'success',
                command: cmd,
                output: stdout,
                error: stderr || null
              });
            }
          });
        } catch (e) {
          console.error(`尝试 ${cmd} 时出错:`, e);
          continue;
        }
      }

      // 如果所有命令都失败
      setTimeout(() => {
        if (!executed) {
          res.status(500).json({ 
            error: 'No Python command available',
            attempted: pythonCommands
          });
        }
      }, 5000);

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
