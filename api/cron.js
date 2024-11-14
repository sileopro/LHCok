const { spawn } = require('child_process');
const path = require('path');

export default async function handler(req, res) {
  console.log('API endpoint hit');
  
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      const scriptPath = path.join(process.cwd(), 'scraper.py');
      
      // 定义可能的 Python 路径
      const pythonPaths = [
        '/usr/bin/python3',
        '/usr/local/bin/python3',
        '/opt/python/bin/python3',
        'python3',
        '/usr/bin/python',
        'python'
      ];

      let executed = false;
      
      for (const pythonPath of pythonPaths) {
        try {
          console.log(`尝试使用 Python 路径: ${pythonPath}`);
          
          // 先检查 Python 是否存在
          const checkPython = spawn('which', [pythonPath]);
          let pythonExists = false;
          
          checkPython.on('close', (code) => {
            pythonExists = code === 0;
          });

          // 等待检查完成
          await new Promise(resolve => setTimeout(resolve, 1000));

          if (!pythonExists) {
            console.log(`${pythonPath} 不存在，尝试下一个路径`);
            continue;
          }

          const python = spawn(pythonPath, [scriptPath]);
          
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
            if (!executed) {
              executed = true;
              res.status(200).json({
                status: code === 0 ? 'success' : 'error',
                pythonPath: pythonPath,
                output: dataString,
                error: errorString || null
              });
            }
          });

          executed = true;
          break;
        } catch (e) {
          console.error(`使用 ${pythonPath} 失败:`, e);
          continue;
        }
      }

      if (!executed) {
        throw new Error('无法找到可用的 Python 安装');
      }

    } catch (error) {
      console.error('执行过程中出错:', error);
      res.status(500).json({ 
        error: error.message,
        stack: error.stack,
        details: '请检查 Python 安装和路径'
      });
    }
  } else {
    res.status(405).json({ error: '方法不允许' });
  }
} 
