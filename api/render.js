const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

module.exports = async (req, res) => {
  try {
    // 调试日志1：记录请求路径（放在最前面）
    console.log('Request URL:', req.url);
    console.log('Request Query:', req.query);
    
    // 处理两种请求方式
    const requestPath = req.url.startsWith('/md/') ? req.url.replace('/md/', '') : req.url;
    console.log('Processed Path:', requestPath);
    const mdPath = req.query.path || requestPath;
    
    // 从GitHub获取Markdown内容
    const githubRawUrl = `https://raw.githubusercontent.com/Yugoge/Personal-Mindmap/refs/heads/main/docs/notion_mermaid_diagram.md`;
    const { default: fetch } = await import('node-fetch');
    const mdResponse = await fetch(githubRawUrl);
    const markdown = await mdResponse.text();
    
    // 调试日志2：验证GitHub内容获取
    console.log('GitHub Content:', markdown.substring(0, 100)); // 显示前100字符
    console.log('Content Length:', markdown.length);

    // 过滤mermaid中的话
    const mermaidCode = markdown.match(/```mermaid([\s\S]*?)```/)[1].trim();
    
    // 
    const inputPath = '/tmp/input.mmd';
    const outputPath = '/tmp/output.svg';
    await fs.writeFile(inputPath, mermaidCode);
    execSync(`npx mmdc -i ${inputPath} -o ${outputPath} -t forest`);

    // 
    execSync(`sed -i 's/<\/svg>/<style>text{font-family: "SansSerif"}<\/style>&/' ${outputPath}`);

    // 
    res.setHeader('Content-Type', 'image/svg+xml');
    res.send(await fs.readFile(outputPath));

  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
};