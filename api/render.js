const { execSync } = require("child_process");
const fs = require("fs-extra");
const path = require("path");

module.exports = async (req, res) => {
  try {
    console.log("✅ Render.js executed!");
    console.log("Request URL:", req.url);
    console.log("Request Query:", req.query);

    // 获取 Markdown 路径
    const requestPath = req.url.startsWith("/md/") ? req.url.replace("/md/", "") : req.url;
    const mdPath = req.query.path || requestPath;
    
    // GitHub 读取 Mermaid 代码
    const githubRawUrl = `https://raw.githubusercontent.com/Yugoge/Personal-Mindmap/main/docs/notion_mermaid_diagram.md`;
    const { default: fetch } = await import("node-fetch");

    const mdResponse = await fetch(githubRawUrl);
    if (!mdResponse.ok) throw new Error(`GitHub fetch error: ${mdResponse.status}`);

    const markdown = await mdResponse.text();
    console.log("GitHub Content (first 100 chars):", markdown.substring(0, 100));

    // 提取 Mermaid 代码块
    const mermaidMatch = markdown.match(/```mermaid([\s\S]*?)```/);
    if (!mermaidMatch) throw new Error("No mermaid code found!");

    const mermaidCode = mermaidMatch[1].trim();
    console.log("Extracted Mermaid Code:", mermaidCode);

    // 临时文件路径（适配 Vercel）
    const tempDir = "/tmp";
    const inputPath = path.join(tempDir, "input.mmd");
    const outputPath = path.join(tempDir, "output.svg");

    await fs.writeFile(inputPath, mermaidCode);

    // 运行 Mermaid CLI
    execSync(`npx mmdc -i ${inputPath} -o ${outputPath} -t forest`, { stdio: "inherit" });

    // 修改 SVG 以适配字体
    execSync(`sed -i 's/<\\/svg>/<style>text{font-family: "SansSerif"}<\\/style>&/' ${outputPath}`);

    // 返回 SVG 图片
    res.setHeader("Content-Type", "image/svg+xml");
    res.send(await fs.readFile(outputPath));

  } catch (error) {
    console.error("❌ Error:", error);
    res.status(500).send(`Error: ${error.message}`);
  }
};