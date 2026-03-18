#!/usr/bin/env python3
"""
可视化 ROLL 框架 dump 的轨迹数据

用法:
    python visualize_rollouts.py /path/to/rollout_dump_data.step_0.jsonl
    python visualize_rollouts.py /path/to/rollout_dump_data.step_0.jsonl --output output.html
    python visualize_rollouts.py /path/to/rollout_dump_data.step_0.jsonl --format markdown
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


def load_jsonl(filepath: str) -> Dict[str, List]:
    """加载 JSONL 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                return json.loads(line)
    return {}


def parse_rollouts(data: Dict[str, List]) -> List[Dict[str, Any]]:
    """将列式数据转换为行式数据（每条轨迹一个 dict）"""
    if not data:
        return []

    # 获取数据长度
    first_key = next(iter(data.keys()))
    num_rollouts = len(data[first_key])

    rollouts = []
    for i in range(num_rollouts):
        rollout = {}
        for key, values in data.items():
            rollout[key] = values[i]
        rollouts.append(rollout)

    return rollouts


def format_trajectory_text(rollout: Dict[str, Any], index: int) -> str:
    """格式化单条轨迹为可读文本"""
    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"轨迹 #{index + 1}")
    lines.append(f"{'='*80}")

    # 显示 rollout_tag
    if 'rollout_tags' in rollout:
        lines.append(f"📌 轨迹标签: {rollout['rollout_tags']}")

    # 解析 save_content
    if 'save_content' in rollout:
        try:
            interactions = json.loads(rollout['save_content'])
            lines.append(f"📊 总步数: {len(interactions)}")

            total_reward = sum(step.get('reward', 0) for step in interactions)
            lines.append(f"🏆 总奖励: {total_reward:.2f}")
            lines.append("")

            for step in interactions:
                step_idx = step.get('step', '?')
                obs = step.get('observation', '')
                response = step.get('llm_response', '')
                reward = step.get('reward', 0)
                feedback_text = step.get('feedback_text', '')
                error_type = step.get('error_type', '')
                improve_hint = step.get('improve_hint', '')

                lines.append(f"--- Step {step_idx} ---")
                lines.append(f"🌍 环境观测:")
                # 缩进观测内容
                for obs_line in obs.split('\n'):
                    lines.append(f"   {obs_line}")

                if response:
                    lines.append(f"🤖 Agent 响应: {response}")
                    lines.append(f"💰 奖励: {reward}")
                if feedback_text:
                    lines.append(f"🧭 反馈: {feedback_text}")
                if error_type:
                    lines.append(f"⚠️ 错误类型: {error_type}")
                if improve_hint:
                    lines.append(f"✅ 建议: {improve_hint}")
                lines.append("")

        except json.JSONDecodeError:
            lines.append(f"save_content: {rollout['save_content'][:500]}...")

    return '\n'.join(lines)


def format_trajectory_markdown(rollout: Dict[str, Any], index: int) -> str:
    """格式化单条轨迹为 Markdown"""
    lines = []
    lines.append(f"\n## 轨迹 #{index + 1}")

    if 'rollout_tags' in rollout:
        lines.append(f"\n**轨迹标签**: `{rollout['rollout_tags']}`")

    if 'save_content' in rollout:
        try:
            interactions = json.loads(rollout['save_content'])
            total_reward = sum(step.get('reward', 0) for step in interactions)
            lines.append(f"\n**总步数**: {len(interactions)} | **总奖励**: {total_reward:.2f}")
            lines.append("")
            
            for step in interactions:
                step_idx = step.get('step', '?')
                obs = step.get('observation', '')
                response = step.get('llm_response', '')
                reward = step.get('reward', 0)
                feedback_text = step.get('feedback_text', '')
                error_type = step.get('error_type', '')
                improve_hint = step.get('improve_hint', '')
                
                lines.append(f"### Step {step_idx}")
                lines.append(f"\n**🌍 环境观测**:\n```\n{obs}\n```")
                
                if response:
                    lines.append(f"\n**🤖 Agent 响应**: `{response}`")
                    lines.append(f"\n**💰 奖励**: {reward}")
                if feedback_text:
                    lines.append(f"\n**🧭 反馈**: {feedback_text}")
                if error_type:
                    lines.append(f"\n**⚠️ 错误类型**: `{error_type}`")
                if improve_hint:
                    lines.append(f"\n**✅ 建议**: {improve_hint}")
                lines.append("")
                
        except json.JSONDecodeError:
            lines.append(f"\n```\n{rollout['save_content'][:500]}...\n```")
    
    return '\n'.join(lines)


def format_trajectory_html(rollout: Dict[str, Any], index: int) -> str:
    """格式化单条轨迹为 HTML"""
    html_parts = []
    
    tag = rollout.get('rollout_tags', f'rollout_{index}')
    
    html_parts.append(f'''
    <div class="rollout" id="rollout-{index}">
        <div class="rollout-header" onclick="toggleRollout({index})">
            <span class="rollout-title">📜 轨迹 #{index + 1}</span>
            <span class="rollout-tag">{tag}</span>
            <span class="toggle-icon">▼</span>
        </div>
        <div class="rollout-content" id="content-{index}">
    ''')
    
    if 'save_content' in rollout:
        try:
            interactions = json.loads(rollout['save_content'])
            total_reward = sum(step.get('reward', 0) for step in interactions)
            
            html_parts.append(f'''
            <div class="rollout-summary">
                <span>📊 总步数: {len(interactions)}</span>
                <span>🏆 总奖励: {total_reward:.2f}</span>
            </div>
            ''')
            
            for step in interactions:
                step_idx = step.get('step', '? ')
                obs = step.get('observation', '').replace('<', '&lt;').replace('>', '&gt;')
                response = step.get('llm_response', '').replace('<', '&lt;').replace('>', '&gt;')
                reward = step.get('reward', 0)
                feedback_text = step.get('feedback_text', '').replace('<', '&lt;').replace('>', '&gt;')
                error_type = step.get('error_type', '').replace('<', '&lt;').replace('>', '&gt;')
                improve_hint = step.get('improve_hint', '').replace('<', '&lt;').replace('>', '&gt;')
                
                reward_class = 'positive' if reward > 0 else ('negative' if reward < 0 else 'neutral')
                
                html_parts.append(f'''
                <div class="step">
                    <div class="step-header">Step {step_idx}</div>
                    <div class="observation">
                        <div class="label">🌍 环境观测</div>
                        <pre>{obs}</pre>
                    </div>
                ''')
                
                if response:
                    html_parts.append(f'''
                    <div class="response">
                        <div class="label">🤖 Agent 响应</div>
                        <code>{response}</code>
                    </div>
                    <div class="reward {reward_class}">
                        💰 奖励: {reward}
                    </div>
                    ''')
                if feedback_text:
                    html_parts.append(f'''
                    <div class="response">
                        <div class="label">🧭 反馈</div>
                        <code>{feedback_text}</code>
                    </div>
                    ''')
                if error_type:
                    html_parts.append(f'''
                    <div class="response">
                        <div class="label">⚠️ 错误类型</div>
                        <code>{error_type}</code>
                    </div>
                    ''')
                if improve_hint:
                    html_parts.append(f'''
                    <div class="response">
                        <div class="label">✅ 建议</div>
                        <code>{improve_hint}</code>
                    </div>
                    ''')
                
                html_parts.append('</div>')
                
        except json.JSONDecodeError:
            html_parts.append(f'<pre>{rollout["save_content"][:500]}...</pre>')
    
    html_parts.append('</div></div>')
    
    return '\n'.join(html_parts)


def generate_html_report(rollouts: List[Dict[str, Any]], output_path: str):
    """生成完整的 HTML 报告"""
    
    html_template = '''
<! DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROLL 轨迹可视化</title>
    <style>
        * {{box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .rollout {{
            background: white;
            margin-bottom: 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .rollout-header {{
            background: #4CAF50;
            color: white;
            padding: 12px 15px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .rollout-header:hover {{
            background: #45a049;
        }}
        .rollout-title {{
            font-weight: bold;
            font-size: 16px;
        }}
        .rollout-tag {{
            background: rgba(255,255,255,0.2);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .toggle-icon {{
            transition: transform 0.3s;
        }}
        .rollout-content {{
            padding: 15px;
            display: none;
        }}
        .rollout-content.active {{
            display: block;
        }}
        .rollout-summary {{
            display: flex;
            gap: 20px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
            margin-bottom: 15px;
        }}
        .step {{
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-bottom: 10px;
            overflow: hidden;
        }}
        .step-header {{
            background: #e3f2fd;
            padding: 8px 12px;
            font-weight: bold;
            color: #1976d2;
        }}
        .observation, .response {{
            padding: 10px 12px;
        }}
        .label {{
            font-weight: bold;
            margin-bottom: 5px;
            color: #666;
        }}
        .observation pre {{
            background: #fafafa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 5px 0 0 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .response code {{
            background: #e8f5e9;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
        }}
        .reward {{
            padding: 8px 12px;
            font-weight: bold;
        }}
        .reward.positive {{ color: #4CAF50; background: #e8f5e9; }}
        .reward.negative {{ color: #f44336; background: #ffebee; }}
        .reward.neutral {{ color: #757575; background: #fafafa; }}
        
        .filter-bar {{
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .filter-bar input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 300px;
        }}
        .filter-bar button {{
            padding: 8px 16px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <h1>🎮 ROLL 轨迹可视化</h1>
    
    <div class="summary">
        <strong>总轨迹数:</strong> {num_rollouts} 条
    </div>
    
    <div class="filter-bar">
        <input type="text" id="search" placeholder="搜索轨迹标签..." onkeyup="filterRollouts()">
        <button onclick="expandAll()">展开全部</button>
        <button onclick="collapseAll()">收起全部</button>
    </div>
    
    <div id="rollouts-container">
        {rollouts_html}
    </div>
    
    <script>
        function toggleRollout(index) {{
            const content = document.getElementById('content-' + index);
            content.classList.toggle('active');
        }}
        
        function expandAll() {{
            document.querySelectorAll('.rollout-content').forEach(el => el.classList.add('active'));
        }}
        
        function collapseAll() {{
            document.querySelectorAll('.rollout-content').forEach(el => el.classList.remove('active'));
        }}
        
        function filterRollouts() {{
            const query = document.getElementById('search').value.toLowerCase();
            document.querySelectorAll('.rollout').forEach(el => {{
                const tag = el.querySelector('.rollout-tag').textContent.toLowerCase();
                el.style.display = tag.includes(query) ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>
    '''
    
    rollouts_html = '\n'.join(
        format_trajectory_html(rollout, i) 
        for i, rollout in enumerate(rollouts)
    )
    
    html_content = html_template.format(
        num_rollouts=len(rollouts),
        rollouts_html=rollouts_html
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 报告已生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='可视化 ROLL 轨迹数据')
    parser.add_argument('input', help='输入的 JSONL 文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['text', 'markdown', 'html'], 
                        default='html', help='输出格式 (默认: html)')
    parser.add_argument('--limit', '-n', type=int, default=None,
                        help='限制显示的轨迹数量')
    
    args = parser.parse_args()
    
    # 加载数据
    print(f"📂 加载文件: {args.input}")
    data = load_jsonl(args.input)
    rollouts = parse_rollouts(data)
    
    if not rollouts:
        print("❌ 没有找到轨迹数据")
        return
    
    print(f"📊 共找到 {len(rollouts)} 条轨迹")
    
    if args.limit:
        rollouts = rollouts[:args.limit]
        print(f"📋 显示前 {args.limit} 条")
    
    # 根据格式输出
    if args.format == 'html':
        output_path = args.output or args.input.replace('.jsonl', '.html')
        generate_html_report(rollouts, output_path)
        
    elif args.format == 'markdown':
        output_path = args.output or args.input.replace('.jsonl', '.md')
        content = f"# ROLL 轨迹可视化\n\n共 {len(rollouts)} 条轨迹\n"
        content += '\n'.join(format_trajectory_markdown(r, i) for i, r in enumerate(rollouts))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Markdown 报告已生成: {output_path}")
        
    else:  # text
        for i, rollout in enumerate(rollouts):
            print(format_trajectory_text(rollout, i))


if __name__ == '__main__':
    main()