#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SECTL 贡献值计算系统
计算公式：贡献值 = （合并PR×5分） + （Commits×3分） + （文档×4分） + （有效Issues×2分） + （Code Review×2分）
时间范围：2025.8.1到2026.1.31
计算仓库：SecRandom, SecRandom-docs
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Any
import os
import sys
import urllib3
from dateutil import parser, relativedelta
from tabulate import tabulate
from tqdm import tqdm

# 禁用SSL证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContributionCalculator:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        # 如果没有token，使用无认证请求（有速率限制）
        if self.github_token:
            self.headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        else:
            self.headers = {
                'Accept': 'application/vnd.github.v3+json'
            }
            print("警告：未设置GITHUB_TOKEN环境变量，将使用无认证请求（有速率限制）")
        self.start_date = datetime(2025, 8, 1, tzinfo=timezone.utc)
        self.end_date = datetime(2026, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
        self.repos = ['SECTL/SecRandom', 'SECTL/SecRandom-docs']
        self.contributors_data = {}
        
    def make_request(self, url: str) -> Dict[str, Any]:
        """发送GitHub API请求"""
        try:
            # 禁用SSL证书验证以解决证书验证失败问题
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {}
    
    def get_repo_contributors(self, repo: str) -> List[Dict[str, Any]]:
        """获取仓库的贡献者列表"""
        url = f"https://api.github.com/repos/{repo}/contributors"
        return self.make_request(url)
    
    def get_user_commits(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在指定仓库的提交记录（排除README.md相关提交）"""
        url = f"https://api.github.com/repos/{repo}/commits"
        params = {
            'author': username,
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        # 禁用SSL证书验证以解决证书验证失败问题
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            commits = response.json()
            # 过滤掉README.md相关的提交
            filtered_commits = []
            readme_keywords = ['readme', 'README.md', 'README', 'readme.md']
            
            for commit in commits:
                commit_message = commit.get('commit', {}).get('message', '').lower()
                # 检查是否包含README相关关键词
                if not any(readme_keyword in commit_message for readme_keyword in readme_keywords):
                    filtered_commits.append(commit)
            
            return filtered_commits
        return []
    
    def get_user_prs(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在指定仓库的PR记录"""
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {
            'state': 'closed',
            'author': username,
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        # 禁用SSL证书验证以解决证书验证失败问题
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            prs = response.json()
            # 只计算已合并的PR
            merged_prs = [pr for pr in prs if pr.get('merged_at') and 
                        self.start_date <= datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00')) <= self.end_date]
            return merged_prs
        return []
    
    def get_user_issues(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在指定仓库的Issues记录"""
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {
            'state': 'closed',
            'creator': username,
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        # 禁用SSL证书验证以解决证书验证失败问题
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_user_assigned_issues(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户被分配处理的Issues记录"""
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {
            'state': 'closed',
            'assignee': username,
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        # 禁用SSL证书验证以解决证书验证失败问题
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_user_opened_prs(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户提出的PR记录（包括所有状态的PR）"""
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {
            'state': 'all',
            'creator': username,
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        # 禁用SSL证书验证以解决证书验证失败问题
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_user_comments(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在Issues和PR中的评论数量"""
        comments = []
        
        # 获取用户评论的Issues
        issues_url = f"https://api.github.com/repos/{repo}/issues/comments"
        params = {
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        response = requests.get(issues_url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            all_comments = response.json()
            user_comments = [comment for comment in all_comments if comment['user']['login'] == username]
            comments.extend(user_comments)
        
        # 获取用户评论的PR
        pr_comments_url = f"https://api.github.com/repos/{repo}/pulls/comments"
        response = requests.get(pr_comments_url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            all_comments = response.json()
            user_comments = [comment for comment in all_comments if comment['user']['login'] == username]
            comments.extend(user_comments)
        
        return comments
    
    def get_user_reviews(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在指定仓库的Code Review记录"""
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {
            'state': 'all',
            'since': self.start_date.isoformat(),
            'until': self.end_date.isoformat()
        }
        # 禁用SSL证书验证以解决证书验证失败问题
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            prs = response.json()
            reviews = []
            for pr in prs:
                reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr['number']}/reviews"
                # 禁用SSL证书验证以解决证书验证失败问题
                reviews_response = requests.get(reviews_url, headers=self.headers, verify=False)
                if reviews_response.status_code == 200:
                    pr_reviews = reviews_response.json()
                    user_reviews = [review for review in pr_reviews if review['user']['login'] == username]
                    reviews.extend(user_reviews)
            return reviews
        return []
    
    def count_documentation_contributions(self, repo: str, username: str) -> int:
        """计算文档贡献数量（仅SECTL/SecRandom-docs仓库的所有提交都算文档贡献）"""
        # 只有SecRandom-docs仓库的提交才算文档贡献
        if repo != 'SECTL/SecRandom-docs':
            return 0
        
        commits = self.get_user_commits(repo, username)
        return len(commits)
    
    def get_code_quality_contributions(self, repo: str, username: str) -> int:
        """计算代码质量贡献（包括测试文件提交、配置文件优化等）"""
        commits = self.get_user_commits(repo, username)
        quality_files = ['test', 'tests', 'config', 'setup', 'requirements', 'pyproject', 'tox', 'pytest']
        
        quality_commits = 0
        for commit in commits:
            commit_message = commit.get('commit', {}).get('message', '').lower()
            if any(quality_file in commit_message for quality_file in quality_files):
                quality_commits += 1
        
        return quality_commits
    
    def get_community_contributions(self, repo: str, username: str) -> int:
        """计算社区贡献（包括回答问题、帮助新手等）"""
        comments = self.get_user_comments(repo, username)
        # 简单计算评论数量作为社区贡献指标
        return len(comments)
    
    def calculate_user_contribution(self, username: str) -> Dict[str, Any]:
        """计算单个用户的贡献值，分别计算两个仓库后合并"""
        repo_data = {}
        total_prs = 0
        total_commits = 0
        total_docs = 0
        total_issues = 0
        total_assigned_issues = 0
        total_opened_prs = 0
        total_reviews = 0
        total_code_quality = 0
        total_community = 0
        
        for repo in self.repos:
            # 获取已合并PR数量
            prs = self.get_user_prs(repo, username)
            repo_prs = len(prs)
            total_prs += repo_prs
            
            # 获取提出的PR数量（所有状态）
            opened_prs = self.get_user_opened_prs(repo, username)
            repo_opened_prs = len(opened_prs)
            total_opened_prs += repo_opened_prs
            
            # 获取Commit数量（已自动排除README.md）
            commits = self.get_user_commits(repo, username)
            repo_commits = len(commits)
            total_commits += repo_commits
            
            # 获取文档贡献数量（仅SecRandom-docs仓库）
            docs = self.count_documentation_contributions(repo, username)
            total_docs += docs
            
            # 获取创建的Issues数量
            issues = self.get_user_issues(repo, username)
            repo_issues = len(issues)
            total_issues += repo_issues
            
            # 获取被分配处理的Issues数量
            assigned_issues = self.get_user_assigned_issues(repo, username)
            repo_assigned_issues = len(assigned_issues)
            total_assigned_issues += repo_assigned_issues
            
            # 获取Code Review数量
            reviews = self.get_user_reviews(repo, username)
            repo_reviews = len(reviews)
            total_reviews += repo_reviews
            
            # 获取代码质量贡献
            code_quality = self.get_code_quality_contributions(repo, username)
            total_code_quality += code_quality
            
            # 获取社区贡献
            community = self.get_community_contributions(repo, username)
            total_community += community
            
            # 计算单个仓库的贡献值（新的评分公式）
            repo_score = (
                repo_prs * 8 +              # 合并PR×8分
                repo_opened_prs * 2 +       # 提出PR×2分
                repo_commits * 3 +          # Commits×3分
                docs * 6 +                  # 文档×6分
                repo_issues * 3 +           # 创建Issues×3分
                repo_assigned_issues * 4 +   # 处理Issues×4分
                repo_reviews * 3 +          # Code Review×3分
                code_quality * 5 +          # 代码质量×5分
                community * 1                # 社区贡献×1分
            )
            
            # 保存仓库数据
            repo_name = repo.split('/')[-1]
            repo_data[repo_name] = {
                'prs': repo_prs,
                'opened_prs': repo_opened_prs,
                'commits': repo_commits,
                'docs': docs,
                'issues': repo_issues,
                'assigned_issues': repo_assigned_issues,
                'reviews': repo_reviews,
                'code_quality': code_quality,
                'community': community,
                'score': repo_score
            }
        
        # 计算总贡献值（新的评分公式）
        contribution_score = (
            total_prs * 8 +              # 合并PR×8分
            total_opened_prs * 2 +       # 提出PR×2分
            total_commits * 3 +          # Commits×3分
            total_docs * 6 +             # 文档×6分
            total_issues * 3 +           # 创建Issues×3分
            total_assigned_issues * 4 +   # 处理Issues×4分
            total_reviews * 3 +          # Code Review×3分
            total_code_quality * 5 +      # 代码质量×5分
            total_community * 1           # 社区贡献×1分
        )
        
        return {
            'username': username,
            'prs': total_prs,
            'opened_prs': total_opened_prs,
            'commits': total_commits,
            'docs': total_docs,
            'issues': total_issues,
            'assigned_issues': total_assigned_issues,
            'reviews': total_reviews,
            'code_quality': total_code_quality,
            'community': total_community,
            'score': contribution_score,
            'repo_data': repo_data
        }
    
    def get_all_contributors(self) -> List[Dict[str, Any]]:
        """获取所有贡献者并计算贡献值（带进度条）"""
        all_users = set()
        
        # 收集所有用户
        for repo in self.repos:
            contributors = self.get_repo_contributors(repo)
            for contributor in contributors:
                all_users.add(contributor['login'])
        
        # 计算每个用户的贡献值（带进度条）
        results = []
        print("🔄 正在计算贡献者数据...")
        for username in tqdm(all_users, desc="处理用户", unit="用户"):
            user_data = self.calculate_user_contribution(username)
            if user_data['score'] > 0:  # 只包含有贡献的用户
                results.append(user_data)
        
        # 按贡献值排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def generate_leaderboard_md(self) -> str:
        """生成贡献值排行榜的Markdown格式（使用tabulate优化版，限制10人，支持折叠）"""
        contributors = self.get_all_contributors()
        
        # 限制最多显示10人
        top_contributors = contributors[:10]
        
        # 使用tabulate生成总体排行榜
        headers = ["排名", "👤 用户名", "🔀 合并PR", "📝 提出PR", "💻 Commits", "📚 文档", "🐛 创建Issue", "🔧 处理Issue", "👀 Review", "⭐ 贡献值"]
        table_data = []
        
        for i, contributor in enumerate(top_contributors, 1):
            table_data.append([
                f"**{i}**",
                f"**{contributor['username']}**",
                str(contributor['prs']),
                str(contributor['opened_prs']),
                str(contributor['commits']),
                str(contributor['docs']),
                str(contributor['issues']),
                str(contributor['assigned_issues']),
                str(contributor['reviews']),
                f"**{contributor['score']}**"
            ])
        
        overall_table = tabulate(table_data, headers=headers, tablefmt="github")
        
        md_content = f"""### 🏆 贡献值排行榜

> 📊 **贡献值计算公式**：贡献值 = （合并PR×8分） + （提出PR×2分） + （Commits×3分） + （文档×6分） + （创建Issue×3分） + （处理Issue×4分） + （Code Review×3分） + （代码质量×5分） + （社区贡献×1分）
> 
> 📅 **统计时间范围**：{self.start_date.strftime('%Y.%m.%d')} - {self.end_date.strftime('%Y.%m.%d')}
> 
> 🏗️ **统计仓库**：{', '.join(self.repos)}
> 
> ⚠️ **注意**：已排除README文件相关贡献统计，最多显示前10名贡献者

#### 📋 总体排行榜（前10名）

{overall_table}

---

#### 📊 各贡献者详细统计（可折叠）

"""
        
        # 添加各贡献者详细统计（支持折叠）
        for i, contributor in enumerate(top_contributors, 1):
            # 生成详细信息表格
            detail_headers = ["仓库", "🔀 合并PR", "📝 提出PR", "💻 Commits", "📚 文档", "🐛 创建Issue", "🔧 处理Issue", "👀 Review", "🔍 代码质量", "🤝 社区贡献", "⭐ 分数"]
            detail_table_data = []
            
            for repo_name, repo_data in contributor['repo_data'].items():
                detail_table_data.append([
                    f"**{repo_name}**",
                    str(repo_data['prs']),
                    str(repo_data['opened_prs']),
                    str(repo_data['commits']),
                    str(repo_data['docs']),
                    str(repo_data['issues']),
                    str(repo_data['assigned_issues']),
                    str(repo_data['reviews']),
                    str(repo_data['code_quality']),
                    str(repo_data['community']),
                    f"**{repo_data['score']}**"
                ])
            
            detail_table = tabulate(detail_table_data, headers=detail_headers, tablefmt="github")
            
            # 添加折叠功能
            md_content += f"""<details>
<summary><strong>👤 第{i}名：{contributor['username']} (总分: {contributor['score']})</strong> - 点击展开详细统计</summary>

{detail_table}

**个人贡献分析：**
- 💪 **最强项**：{self._get_strongest_contribution(contributor)}
- 📈 **主要贡献领域**：{self._get_main_contribution_area(contributor)}
- 🎯 **建议提升方向**：{self._get_improvement_suggestion(contributor)}

</details>

"""
        
        # 如果有超过10人，显示提示
        if len(contributors) > 10:
            md_content += f"""*💡 提示：共有 {len(contributors)} 位贡献者，此处仅显示前10名。完整数据请查看控制台输出。*

"""
        
        md_content += f"*📅 最后更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return md_content
    
    def _get_strongest_contribution(self, contributor: Dict[str, Any]) -> str:
        """获取贡献者最强项"""
        contributions = {
            '合并PR': contributor['prs'],
            '提出PR': contributor['opened_prs'],
            '代码提交': contributor['commits'],
            '文档贡献': contributor['docs'],
            '创建Issue': contributor['issues'],
            '处理Issue': contributor['assigned_issues'],
            '代码审查': contributor['reviews'],
            '代码质量': contributor['code_quality'],
            '社区贡献': contributor['community']
        }
        
        strongest = max(contributions, key=contributions.get)
        if contributions[strongest] > 0:
            return f"{strongest} ({contributions[strongest]}次)"
        else:
            return "暂无突出贡献"
    
    def _get_main_contribution_area(self, contributor: Dict[str, Any]) -> str:
        """获取主要贡献领域"""
        # 根据不同维度的贡献判断主要领域
        if contributor['prs'] > contributor['commits'] and contributor['prs'] > 0:
            return "代码开发与功能实现"
        elif contributor['docs'] > 0 and contributor['docs'] >= contributor['prs']:
            return "文档编写与维护"
        elif contributor['assigned_issues'] > 0 and contributor['assigned_issues'] >= contributor['issues']:
            return "问题处理与Bug修复"
        elif contributor['issues'] > 0:
            return "问题发现与反馈"
        elif contributor['reviews'] > 0:
            return "代码审查与质量把控"
        elif contributor['code_quality'] > 0:
            return "代码质量改进"
        else:
            return "多方面贡献"
    
    def _get_improvement_suggestion(self, contributor: Dict[str, Any]) -> str:
        """获取改进建议"""
        suggestions = []
        
        if contributor['prs'] == 0:
            suggestions.append("可以尝试提交PR参与代码开发")
        if contributor['docs'] == 0:
            suggestions.append("可以参与文档编写和完善")
        if contributor['assigned_issues'] == 0:
            suggestions.append("可以参与Issue处理和Bug修复")
        if contributor['reviews'] == 0:
            suggestions.append("可以参与代码审查帮助提升代码质量")
        
        if not suggestions:
            return "继续保持良好的贡献节奏，可以尝试更多类型的贡献"
        else:
            return "、".join(suggestions[:2])  # 最多返回2个建议
    
    def update_readme(self, readme_path: str):
        """更新README文件，插入贡献值排行榜"""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 生成新的贡献值排行榜
            leaderboard_md = self.generate_leaderboard_md()
            
            # 查找插入位置（在文档章节之前）
            insert_marker = "## 📄 文档"
            if insert_marker in content:
                # 替换旧的贡献值排行榜（如果存在）
                old_leaderboard_start = "### 🏆 贡献值排行榜"
                old_leaderboard_end = "### 星标历史 ✨"
                
                if old_leaderboard_start in content:
                    # 删除旧的贡献值排行榜
                    start_idx = content.find(old_leaderboard_start)
                    end_idx = content.find(old_leaderboard_end)
                    content = content[:start_idx] + content[end_idx:]
                
                # 插入新的贡献值排行榜
                content = content.replace(insert_marker, leaderboard_md + "\n\n" + insert_marker)
            
            # 写入文件
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("README.md 更新成功！")
            
        except Exception as e:
            print(f"更新README.md失败: {e}")

if __name__ == "__main__":
    calculator = ContributionCalculator()
    
    # 更新README.md
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
    print(f"🔄 正在更新README.md文件: {readme_path}")
    calculator.update_readme(readme_path)
    print("✅ README.md更新完成！")
    
    # 输出贡献值数据
    contributors = calculator.get_all_contributors()
    
    # 使用tabulate生成控制台表格
    print("\n🏆 贡献值排行榜：")
    print("=" * 100)
    
    headers = ["排名", "用户名", "合并PR", "提出PR", "Commit", "文档", "创建Issue", "处理Issue", "Review", "代码质量", "社区", "总分"]
    table_data = []
    
    # 限制控制台输出也只显示前10名
    display_contributors = contributors[:10]
    
    for i, contributor in enumerate(display_contributors, 1):
        table_data.append([
            str(i),
            contributor['username'],
            str(contributor['prs']),
            str(contributor['opened_prs']),
            str(contributor['commits']),
            str(contributor['docs']),
            str(contributor['issues']),
            str(contributor['assigned_issues']),
            str(contributor['reviews']),
            str(contributor['code_quality']),
            str(contributor['community']),
            str(contributor['score'])
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # 如果有超过10人，显示提示
    if len(contributors) > 10:
        print(f"\n💡 提示：共有 {len(contributors)} 位贡献者，此处仅显示前10名。")
    
    print("\n" + "=" * 100)
    print("📊 各仓库详细统计：")
    print("=" * 100)
    
    # 输出各仓库详细统计（也只显示前10名）
    for contributor in display_contributors:
        print(f"\n👤 {contributor['username']} (总分: {contributor['score']})")
        
        repo_headers = ["仓库", "合并PR", "提出PR", "Commit", "文档", "创建Issue", "处理Issue", "Review", "代码质量", "社区", "分数"]
        repo_table_data = []
        
        for repo_name, repo_data in contributor['repo_data'].items():
            repo_table_data.append([
                repo_name,
                str(repo_data['prs']),
                str(repo_data['opened_prs']),
                str(repo_data['commits']),
                str(repo_data['docs']),
                str(repo_data['issues']),
                str(repo_data['assigned_issues']),
                str(repo_data['reviews']),
                str(repo_data['code_quality']),
                str(repo_data['community']),
                str(repo_data['score'])
            ])
        
        print(tabulate(repo_table_data, headers=repo_headers, tablefmt="pretty"))
        
        # 添加个人贡献分析
        print(f"\n📈 个人贡献分析：")
        print(f"   💪 最强项：{calculator._get_strongest_contribution(contributor)}")
        print(f"   🎯 主要领域：{calculator._get_main_contribution_area(contributor)}")
        print(f"   📝 改进建议：{calculator._get_improvement_suggestion(contributor)}")
    
    print("=" * 60)
    print(f"统计时间：{calculator.start_date.strftime('%Y-%m-%d')} 至 {calculator.end_date.strftime('%Y-%m-%d')}")
    print(f"统计仓库：{', '.join(calculator.repos)}")