const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

module.exports = async (req, res) => {
  try {
    const mdPath = req.query.path;
    
    // 校验路径参数
    if (!mdPath) {
      return res.status(400).send('Missing path parameter');
    }

    // 动态构建GitHub URL
    const githubRawUrl = `https://raw.githubusercontent.com/Yugoge/Personal-Mindmap/main/docs/${mdPath}.md`;
    
    const { default: fetch } = await import('node-fetch');
    const mdResponse = await fetch(githubRawUrl);
    
    if (!mdResponse.ok) {
      return res.status(404).send('Markdown file not found');
    }

    const markdown = await mdResponse.text();

    // 健壮的mermaid代码提取
    const mermaidMatch = markdown.match(/```mermaid([\s\S]*?)```/)[1].trim();
    if (!mermaidMatch) {
      return res.status(400).send('No mermaid code block found');
    }

    // 文件操作使用同步API
    const inputPath = '/tmp/input.mmd';
    const outputPath = '/tmp/output.svg';
    await fs.writeFile(inputPath, mermaidMatch[1].trim());
    
    // 使用本地安装的mmdc
    execSync(`npx mmdc -i ${inputPath} -o ${outputPath} -t forest`);
    
    // SVG字体优化
    execSync(`sed -i 's/<\/svg>/<style>text{font-family:"Segoe UI"}</style>&/' ${outputPath}`);

    res.setHeader('Content-Type', 'image/svg+xml');
    res.send(await fs.readFile(outputPath));

  } catch (error) {
    console.error('Error:', error);
    res.status(500).send(`Error: ${error.message}`);
  }
};