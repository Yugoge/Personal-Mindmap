const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

module.exports = async (req, res) => {
  try {
    // 处理两种请求方式
    const mdPath = req.query.path || req.url.replace('/md/', '');
    
    // 从GitHub获取Markdown内容
    const githubRawUrl = `https://raw.githubusercontent.com/${process.env.GITHUB_REPO}/main/${mdPath}`;
    const { default: fetch } = await import('node-fetch');
    const mdResponse = await fetch(githubRawUrl);
    const markdown = await mdResponse.text();

    // 过滤mermaid 中的话
    const mermaidCode = markdown.match(/```mermaid([\s\S]*?)```/)[1].trim();
    
    // 前原文数
    const inputPath = '/tmp/input.mmd';
    const outputPath = '/tmp/output.svg';
    await fs.writeFile(inputPath, mermaidCode);
    execSync(`npx mmdc -i ${inputPath} -o ${outputPath} -t forest`);

    // 中文加入一次
    execSync(`sed -i 's/<\/svg>/<style>text{font-family: "SansSerif"}<\/style>&/' ${outputPath}`);

    // 从加入镹—结束
    res.setHeader('Content-Type', 'image/svg+xml');
    res.send(await fs.readFile(outputPath));

  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
};