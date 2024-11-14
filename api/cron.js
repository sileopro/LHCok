const fetch = require('node-fetch');

export default async function handler(req, res) {
  if (req.method === 'POST' || req.method === 'GET') {
    try {
      console.log('开始执行爬虫脚本...');
      
      const response = await fetch(`${req.headers.host}/api/run`);
      const data = await response.json();
      
      res.status(200).json(data);
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
