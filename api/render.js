const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

module.exports = async (req, res) => {
  try {
    const mdPath = req.query.path || req.url.replace('/md/', '');
    const githubRawUrl = `https://raw.githubusercontent.com/${process.env.GITHUB_REPO}/main/${mdPath}`;
    
    // 获取Markdown内容
    const { default: fetch } = await import('node-fetch');
    const mdResponse = await fetch(githubRawUrl);
    const markdown = await mdResponse.text();

    // 提取mermaid代码
    const mermaidCode = markdown.match(/