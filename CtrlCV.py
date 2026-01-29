#!/usr/bin/env python3

import json
import os
import re
import yaml

def load_yaml(file_path):
    """加载YAML文件，支持制表符缩进"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 将制表符转换为4个空格（YAML标准）
    # 注意：YAML规范要求使用空格，但我们可以预处理转换
    content = content.replace('\t', '    ')
    # 使用safe_load解析
    return yaml.safe_load(content)

def sanitize_id(text):
    """将文本转换为有效的HTML ID"""
    return re.sub(r'[^\w\-]', '', text.replace(' ', '_').replace('-', '_'))

def parse_journal(journal_data):
    """解析期刊数据"""
    html_lines = []
    
    if isinstance(journal_data, list):
        for item in journal_data:
            if isinstance(item, dict):
                for journal_name, journal_info in item.items():
                    safe_id = sanitize_id(journal_name)
                    
                    html_lines.append(f'<div class="spacer"></div>')
                    html_lines.append(f'<div class="journal-item" id="journal-{safe_id}">')
                    html_lines.append(f'  <button class="list-btn" onclick="copyLine(this)">-</button>')
                    html_lines.append(f'  <span class="journal-name">{journal_name}</span>')
                    html_lines.append(f'</div>')
                    
                    if isinstance(journal_info, dict):
                        for key, value in journal_info.items():
                            if key == '文章':
                                html_lines.append(f'<div class="line l1">{key}</div>')
                                for article in value:
                                    if isinstance(article, dict):
                                        for article_title, _ in article.items():
                                            article_id = sanitize_id(article_title)
                                            html_lines.append(f'<div class="line l2">')
                                            html_lines.append(f'  <button class="list-btn" onclick="copyLine(this)">-</button>')
                                            html_lines.append(f'  <a onclick="scrollToArticle(\'{article_id}\')">{article_title}</a>')
                                            html_lines.append(f'</div>')
                                    else:
                                        article_id = sanitize_id(article)
                                        html_lines.append(f'<div class="line l2">')
                                        html_lines.append(f'  <button class="list-btn" onclick="copyLine(this)">-</button>')
                                        html_lines.append(f'  <a onclick="scrollToArticle(\'{article_id}\')">{article}</a>')
                                        html_lines.append(f'</div>')
                            else:
                                html_lines.append(f'<div class="line l1">{key}<button onclick="copyValue(this)">:</button>{value}</div>')
    
    return html_lines

def parse_paper(paper_data):
    """解析论文数据"""
    html_lines = []
    
    if isinstance(paper_data, list):
        for paper in paper_data:
            if isinstance(paper, dict):
                for paper_title, paper_info in paper.items():
                    safe_id = sanitize_id(paper_title)
                    
                    html_lines.append(f'<div class="spacer"></div>')
                    html_lines.append(f'<div class="article-item" id="{safe_id}">')
                    html_lines.append(f'  <button class="list-btn" onclick="copyLine(this)">-</button>')
                    html_lines.append(f'  <span class="article-title">{paper_title}</span>')
                    html_lines.append(f'</div>')
                    
                    if isinstance(paper_info, dict):
                        for key, value in paper_info.items():
                            if key == '摘要':
                                html_lines.append(f'<div class="line l1">{key}<button onclick="copyAbstract(this)">:</button></div>')
                                if isinstance(value, str):
                                    cleaned_value = value.strip()
                                    html_lines.append(f'<div class="line l2 multiline">{cleaned_value}</div>')
                            elif key == '期刊':
                                html_lines.append(f'<div class="line l1">{key}<button onclick="copyValue(this)">:</button><a onclick="scrollToJournal(\'{value}\')">{value}</a></div>')
                            elif isinstance(value, list):
                                # 收集所有下级item的文本
                                item_texts = []
                                for item in value:
                                    if isinstance(item, dict):
                                        # 字典：取第一个key作为文本
                                        for sub_key, _ in item.items():
                                            item_texts.append(sub_key)
                                            break  # 只取第一个key
                                    else:
                                        # 字符串：直接添加
                                        item_texts.append(str(item))
                                # 创建列表项，包含多个复制按钮
                                # 使用JSON格式存储，避免分号冲突
                                items_json = json.dumps(item_texts, ensure_ascii=False)
                                html_lines.append(f'<div class="line l1">{key}')
                                # 五种连接符：全角顿号、全角逗号、全角分号、半角逗号、半角分号
                                separators = ['、', '，', '；', ', ', '; ']
                                for sep in separators:
                                    html_lines.append(f'  <button class="copy-all-btn" onclick="copyAllItems(this, \'{sep}\')" data-items=\'{items_json}\'>{sep}</button>')                              
                                html_lines.append(f'</div>')
                                for item in value:
                                    if isinstance(item, dict):
                                        for sub_key, sub_value in item.items():
                                            html_lines.append(f'<div class="line l2">')
                                            html_lines.append(f'  <button class="list-btn" onclick="copyLine(this)">-</button>')
                                            html_lines.append(f'  <span class="sub-item">{sub_key}</span>')
                                            html_lines.append(f'</div>')
                                            if isinstance(sub_value, dict):
                                                for s_key, s_value in sub_value.items():
                                                    html_lines.append(f'<div class="line l3">{s_key}<button onclick="copyValue(this)">:</button>{s_value}</div>')
                                            elif isinstance(sub_value, str):
                                                html_lines.append(f'<div class="line l3">值<button onclick="copyValue(this)">:</button>{sub_value}</div>')
                                    else:
                                        html_lines.append(f'<div class="line l2">')
                                        html_lines.append(f'  <button class="list-btn" onclick="copyLine(this)">-</button>')
                                        html_lines.append(f'  <span class="list-item">{item}</span>')
                                        html_lines.append(f'</div>')
                            elif isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    html_lines.append(f'<div class="line l1">{sub_key}<button onclick="copyValue(this)">:</button>{sub_value}</div>')
                            else:
                                html_lines.append(f'<div class="line l1">{key}<button onclick="copyValue(this)">:</button>{value}</div>')
    
    return html_lines

def generate_html(journals_yaml, papers_yaml):
    """生成完整的HTML页面"""
    # 加载YAML数据
    journals = load_yaml(journals_yaml)
    papers = load_yaml(papers_yaml)
    
    # 解析数据
    left_panel_html = parse_journal(journals)
    right_panel_html = parse_paper(papers)
    
    # 生成HTML模板
    newline = "\n            "
    html_template = f'''<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin:0; padding:20px; font-family:"Consolas","Monaco","Microsoft YaHei UI","Microsoft YaHei",monospace,sans-serif; font-size:14px; }}
        .container {{ display:flex; height:90vh; gap:20px; }}
        .left, .right {{ flex:1; overflow-y:auto; padding:10px; border:1px solid #ccc; }}
        .line {{ margin-bottom:6px; line-height: 1.4; }}
        .l0 {{ margin-left:0; }}
        .l1 {{ margin-left:2em; }}
        .l2 {{ margin-left:4em; }}
        .l3 {{ margin-left:6em; }}
        .l4 {{ margin-left:8em; }}
        .copy-all-btn {{ margin-left:0px; width:1.2em; height:16px; line-height:16px; padding:0; text-align:center; }}
        button {{ cursor:pointer; margin:0 2px; padding:0 3px; font-family:"Consolas","Monaco","Microsoft YaHei UI","Microsoft YaHei",monospace,sans-serif; border:1px solid #ccc; background:#f5f5f5; }}
        a {{ color:blue; text-decoration:none; cursor:pointer; }}
        a:hover {{ text-decoration:underline; }}
        .highlight {{ background-color:yellow; animation: highlightFade 2s forwards; }}
        @keyframes highlightFade {{
            0% {{ background-color: yellow; }}
            100% {{ background-color: transparent; }}
        }}
        .multiline {{ white-space: pre-line; margin-left: 4em; line-height: 1.4; }}
        .list-btn {{ margin-right: 2px; }}
        .spacer {{ margin-top: 10px; }}
        .journal-item, .article-item {{ margin-bottom: 8px; line-height: 1.5; }}
        .copy-content {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 左栏：期刊信息 -->
        <div class="left" id="left-panel">
            {newline.join(left_panel_html)}
        </div>
        
        <!-- 右栏：文章信息 -->
        <div class="right" id="right-panel">
            {newline.join(right_panel_html)}
        </div>
    </div>
    
    <script>
        let copyTimeouts = new Map();
        
        function copyValue(button) {{
            const line = button.parentElement;
            let text = "";
            
            let node = button.nextSibling;
            while (node) {{
                if (node.nodeType === 3) {{
                    text += node.textContent;
                }} else if (node.nodeType === 1 && node.tagName === 'A') {{
                    text += node.textContent;
                }} else if (node.nodeType === 1 && node.tagName === 'SPAN') {{
                    text += node.textContent;
                }}
                node = node.nextSibling;
            }}
            
            text = text.trim();
            
            navigator.clipboard.writeText(text).then(() => {{
                if (copyTimeouts.has(button)) {{
                    clearTimeout(copyTimeouts.get(button));
                }}
                
                const originalText = button.textContent;
                button.textContent = '#';
                
                const timeoutId = setTimeout(() => {{
                    button.textContent = originalText;
                    copyTimeouts.delete(button);
                }}, 1000);
                
                copyTimeouts.set(button, timeoutId);
            }});
        }}
        
        function copyLine(button) {{
            // 找到按钮所在的容器
            const container = button.parentElement;
            
            // 找到容器中要复制的实际内容
            let text = "";
            let contentFound = false;
            
            // 遍历所有子节点
            for (let child of container.children) {{
                if (child === button) continue;  // 跳过按钮本身
                
                if (child.classList && child.classList.contains('copy-content')) {{
                    // 如果有隐藏的复制内容元素，直接使用它
                    text = child.textContent.trim();
                    contentFound = true;
                    break;
                }}
                
                if (child.tagName === 'A' || child.tagName === 'SPAN') {{
                    text = child.textContent.trim();
                    contentFound = true;
                    break;
                }}
            }}
            
            // 如果没有找到特定的内容元素，则提取所有文本内容
            if (!contentFound) {{
                // 收集所有文本节点
                const walker = document.createTreeWalker(
                    container,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let nodes = [];
                let node = walker.nextNode();
                while (node) {{
                    const trimmed = node.textContent.trim();
                    if (trimmed) {{
                        nodes.push(trimmed);
                    }}
                    node = walker.nextNode();
                }}
                
                // 合并文本节点，跳过按钮前的文本
                for (let i = 0; i < nodes.length; i++) {{
                    if (!nodes[i].includes('-') && nodes[i] !== ':') {{
                        text = nodes[i];
                        break;
                    }}
                }}
            }}
            
            navigator.clipboard.writeText(text).then(() => {{
                if (copyTimeouts.has(button)) {{
                    clearTimeout(copyTimeouts.get(button));
                }}
                
                const originalText = button.textContent;
                button.textContent = '#';
                
                const timeoutId = setTimeout(() => {{
                    button.textContent = originalText;
                    copyTimeouts.delete(button);
                }}, 1000);
                
                copyTimeouts.set(button, timeoutId);
            }});
        }}
        
        function copyAbstract(button) {{
            const line = button.parentElement;
            const abstractDiv = line.nextElementSibling;
            
            if (abstractDiv && abstractDiv.classList.contains('multiline')) {{
                const text = abstractDiv.textContent.trim();
                
                navigator.clipboard.writeText(text).then(() => {{
                    if (copyTimeouts.has(button)) {{
                        clearTimeout(copyTimeouts.get(button));
                    }}
                    
                    const originalText = button.textContent;
                    button.textContent = '#';
                    
                    const timeoutId = setTimeout(() => {{
                        button.textContent = originalText;
                        copyTimeouts.delete(button);
                    }}, 1000);
                    
                    copyTimeouts.set(button, timeoutId);
                }});
            }}
        }}
        
        function copyAllItems(button, separator) {{
            // 从data-items属性获取JSON数组
            const itemsJson = button.getAttribute('data-items');
            
            if (itemsJson) {{
                try {{
                    // 解析JSON数组
                    const itemsArray = JSON.parse(itemsJson);
                    const combinedText = itemsArray.join(separator);
                    
                    navigator.clipboard.writeText(combinedText).then(() => {{
                        if (copyTimeouts.has(button)) {{
                            clearTimeout(copyTimeouts.get(button));
                        }}
                        
                        const originalText = button.textContent;
                        button.textContent = '#';
                        
                        const timeoutId = setTimeout(() => {{
                            button.textContent = originalText;
                            copyTimeouts.delete(button);
                        }}, 1000);
                        
                        copyTimeouts.set(button, timeoutId);
                    }});
                }} catch (error) {{
                    console.error('解析items数据失败:', error);
                }}
            }}
        }}
        
        function scrollToArticle(articleId) {{
            const rightPanel = document.getElementById('right-panel');
            const target = document.getElementById(articleId);
            
            if (target) {{
                document.querySelectorAll('.highlight').forEach(el => {{
                    el.classList.remove('highlight');
                }});
                
                target.classList.add('highlight');
                rightPanel.scrollTop = target.offsetTop - 50;
            }}
        }}
        
        function scrollToJournal(journalName) {{
            const leftPanel = document.getElementById('left-panel');
            const journalId = 'journal-' + journalName
                .replace(/ /g, '_')  // 空格转下划线
                .replace(/-/g, '_')  // 连字符转下划线
                .replace(/[^\\w]/g, '');  // 移除其他特殊字符
            const target = document.getElementById(journalId);
            
            if (target) {{
                document.querySelectorAll('.highlight').forEach(el => {{
                    el.classList.remove('highlight');
                }});
                
                target.classList.add('highlight');
                leftPanel.scrollTop = target.offsetTop - 50;
            }}
        }}
        
        document.addEventListener('animationend', function(event) {{
            if (event.animationName === 'highlightFade') {{
                event.target.classList.remove('highlight');
            }}
        }});
    </script>
</body>
</html>'''
    
    return html_template

def main():
    """主函数"""
    # 输入文件路径
    journals_file = "Journals.yaml"
    papers_file = "Papers.yaml"
    output_file = "ExCiting.html"
    
    # 检查输入文件是否存在
    if not os.path.exists(journals_file):
        with open(journals_file, 'w', encoding='utf-8') as f:
            f.write("""- ACM:
    名称: ACM计算概览
    文章:
        - 神经网络崛起
        - 量子计算综述
- IEEE:
    名称: IEEE汇刊
    文章:
        - 5G网络安全
        - 物联网协议分析
- Nature:
    名称: 自然通讯
    文章:
        - 基因编辑进展
""")
    
    if not os.path.exists(papers_file):
        with open(papers_file, 'w', encoding='utf-8') as f:
            f.write("""- 神经网络崛起:
    标题: 神经网络崛起
    年份: 2023
    期刊: ACM
    DOI: 10.1145/123456
    作者:
        - 张三:
            第一作者: 是
            单位: 清华大学
        - 李四:
            第一作者: 否
            单位: 北京大学
    关键词:
        - 神经网络
        - 深度学习
        - 人工智能
    摘要: |
        本文系统回顾了神经网络近年来的发展历程。
        从早期的感知机模型到如今的深度学习架构，
        神经网络在计算机视觉、自然语言处理等领域
        取得了突破性进展。研究重点包括卷积神经网络、
        循环神经网络、注意力机制等核心技术的演进。
- 量子计算综述:
    标题: 量子计算综述
    年份: 2022
    期刊: ACM
- 5G网络安全:
    标题: 5G网络安全
    年份: 2021
    期刊: IEEE
- 物联网协议分析:
    标题: 物联网协议分析
    年份: 2020
    期刊: IEEE
- 基因编辑进展:
    标题: 基因编辑进展
    年份: 2023
    期刊: Nature
""")
    
    # 生成HTML
    html_content = generate_html(journals_file, papers_file)
    
    # 保存输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML已生成: {output_file}")
    print(f"请在浏览器中打开 {output_file} 查看结果")

if __name__ == "__main__":
    main()