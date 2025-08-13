#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SECTL 贡献值计算系统
计算公式：贡献值 = （合并PR×10分） + （提出PR×3分） + （Commits×2分） + （文档×5分） + （创建Issue×3分） + （处理Issue×5分） + （Code Review×2分）
时间范围：2025.8.1到2026.1.31
计算仓库：SECTL/SecRandom, SECTL/SecRandom-docs
"""

import requests
import json
from datetime import datetime, timezone, timedelta
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
        # 设置为中国时间（UTC+8）
        china_tz = timezone(timedelta(hours=8))
        self.start_date = datetime(2025, 8, 1, tzinfo=china_tz)
        self.end_date = datetime(2026, 1, 31, 23, 59, 59, tzinfo=china_tz)
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
        """获取仓库的贡献者列表（排除机器人用户）"""
        url = f"https://api.github.com/repos/{repo}/contributors"
        contributors = self.make_request(url)
        
        # 排除机器人用户和特定用户
        excluded_users = {'actions-user', 'github-actions[bot]', 'dependabot[bot]', 'web-flow'}
        filtered_contributors = []
        
        for contributor in contributors:
            if isinstance(contributor, dict) and contributor.get('login') not in excluded_users:
                filtered_contributors.append(contributor)
        
        return filtered_contributors
    
    def get_user_commits(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在指定仓库的提交记录（排除README.md相关提交）"""
        all_commits = []
        page = 1
        
        while True:
            url = f"https://api.github.com/repos/{repo}/commits"
            # 转换为UTC时间进行GitHub API查询
            utc_start = self.start_date.astimezone(timezone.utc)
            utc_end = self.end_date.astimezone(timezone.utc)
            params = {
                'author': username,
                'since': utc_start.isoformat(),
                'until': utc_end.isoformat(),
                'per_page': 100,
                'page': page
            }
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            if response.status_code == 200:
                commits = response.json()
                if not commits:
                    break
                    
                for commit in commits:
                    # 获取提交详细信息
                    commit_detail = self.make_request(commit.get('url', ''))
                    if commit_detail:
                        files = commit_detail.get('files', [])
                        
                        # 检查是否有README相关文件
                        has_readme_file = False
                        for file_info in files:
                            filename = file_info.get('filename', '').lower()
                            if 'readme' in filename:
                                has_readme_file = True
                                break
                        
                        # 如果没有README文件，则保留该提交
                        if not has_readme_file:
                            all_commits.append(commit)
                
                page += 1
            else:
                break
        
        return all_commits
    
    def get_user_merged_prs(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户已合并的PR记录（正确方式）"""
        url = f"https://api.github.com/search/issues"
        # 转换为UTC时间进行GitHub API查询
        utc_start = self.start_date.astimezone(timezone.utc)
        utc_end = self.end_date.astimezone(timezone.utc)
        params = {
            'q': f'repo:{repo} type:pr author:{username} is:merged merged:{utc_start.strftime("%Y-%m-%d")}..{utc_end.strftime("%Y-%m-%d")}',
            'per_page': 100
        }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    
    def get_user_opened_prs(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户提出的所有PR记录（正确方式）"""
        url = f"https://api.github.com/search/issues"
        # 转换为UTC时间进行GitHub API查询
        utc_start = self.start_date.astimezone(timezone.utc)
        utc_end = self.end_date.astimezone(timezone.utc)
        params = {
            'q': f'repo:{repo} type:pr author:{username} created:{utc_start.strftime("%Y-%m-%d")}..{utc_end.strftime("%Y-%m-%d")}',
            'per_page': 100
        }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    
    def get_user_created_issues(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户创建的Issues记录（正确方式）"""
        url = f"https://api.github.com/search/issues"
        # 转换为UTC时间进行GitHub API查询
        utc_start = self.start_date.astimezone(timezone.utc)
        utc_end = self.end_date.astimezone(timezone.utc)
        params = {
            'q': f'repo:{repo} type:issue author:{username} created:{utc_start.strftime("%Y-%m-%d")}..{utc_end.strftime("%Y-%m-%d")}',
            'per_page': 100
        }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    
    def get_user_assigned_issues(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户被分配的Issues记录（正确方式）"""
        url = f"https://api.github.com/search/issues"
        # 转换为UTC时间进行GitHub API查询
        utc_start = self.start_date.astimezone(timezone.utc)
        utc_end = self.end_date.astimezone(timezone.utc)
        params = {
            'q': f'repo:{repo} type:issue assignee:{username} closed:{utc_start.strftime("%Y-%m-%d")}..{utc_end.strftime("%Y-%m-%d")}',
            'per_page': 100
        }
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []
    
        # 该方法已被更优实现替代，故移除重复定义


    
    def get_user_comments(self, repo: str, username: str) -> List[Dict[str, Any]]:
        """获取用户在Issues和PR中的评论数量"""
        comments = []
        
        # 获取用户评论的Issues
        issues_url = f"https://api.github.com/repos/{repo}/issues/comments"
        # 转换为UTC时间进行GitHub API查询
        utc_start = self.start_date.astimezone(timezone.utc)
        utc_end = self.end_date.astimezone(timezone.utc)
        params = {
            'since': utc_start.isoformat(),
            'until': utc_end.isoformat()
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
    
    # 该方法已被get_code_quality_contributions替代，故注释
    # def get_user_reviews(self, repo: str, username: str) -> List[Dict[str, Any]]:
    #     """获取用户在指定仓库的Code Review记录"""
    #     url = f"https://api.github.com/repos/{repo}/pulls"
    #     params = {
    #         'state': 'all',
    #         'since': self.start_date.isoformat(),
    #         'until': self.end_date.isoformat()
    #     }
    #     # 禁用SSL证书验证以解决证书验证失败问题
    #     response = requests.get(url, headers=self.headers, params=params, verify=False)
    #     if response.status_code == 200:
    #         prs = response.json()
    #         reviews = []
    #         for pr in prs:
    #             reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr['number']}/reviews"
    #             # 禁用SSL证书验证以解决证书验证失败问题
    #             reviews_response = requests.get(reviews_url, headers=self.headers, verify=False)
    #             if reviews_response.status_code == 200:
    #                 pr_reviews = reviews_response.json()
    #                 user_reviews = [review for review in pr_reviews if review['user']['login'] == username]
    #                 reviews.extend(user_reviews)
    #         return reviews
    #     return []
    
    def count_documentation_contributions(self, repo: str, username: str) -> int:
        """计算文档贡献数量（README.md、changelog、docs/、.md 相关提交）"""
        all_doc_commits = []
        page = 1
        
        while True:
            url = f"https://api.github.com/repos/{repo}/commits"
            # 转换为UTC时间进行GitHub API查询
            utc_start = self.start_date.astimezone(timezone.utc)
            utc_end = self.end_date.astimezone(timezone.utc)
            params = {
                'author': username,
                'since': utc_start.isoformat(),
                'until': utc_end.isoformat(),
                'per_page': 100,
                'page': page
            }
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            if response.status_code == 200:
                commits = response.json()
                if not commits:
                    break
                
                for commit in commits:
                    commit_detail = self.make_request(commit.get('url', ''))
                    if commit_detail:
                        files = commit_detail.get('files', [])
                        # 检查是否包含文档文件
                        for file_info in files:
                            filename = file_info.get('filename', '').lower()
                            if any(doc_file in filename for doc_file in ['readme', 'changelog', 'docs/', '.md']):
                                all_doc_commits.append(commit)
                                break
                
                page += 1
            else:
                break
        
        return len(all_doc_commits)
    
    def get_code_quality_contributions(self, repo: str, username: str) -> int:
        """计算代码质量贡献（Code Review）"""
        all_reviews = []
        page = 1
        
        # 搜索指定时间范围内的所有PR（转换为UTC时间进行GitHub API查询）
        utc_start = self.start_date.astimezone(timezone.utc)
        utc_end = self.end_date.astimezone(timezone.utc)
        pr_search_url = "https://api.github.com/search/issues"
        pr_query = f"repo:{repo} type:pr updated:{utc_start.strftime('%Y-%m-%d')}..{utc_end.strftime('%Y-%m-%d')}"
        
        while True:
            params = {
                'q': pr_query,
                'per_page': 100,
                'page': page
            }
            response = requests.get(pr_search_url, headers=self.headers, params=params, verify=False)
            if response.status_code == 200:
                prs = response.json().get('items', [])
                if not prs:
                    break
                
                for pr in prs:
                    pr_number = pr.get('number')
                    if pr_number:
                        # 获取PR的review记录
                        review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
                        reviews = self.make_request(review_url)
                        if reviews:
                            for review in reviews:
                                reviewer = review.get('user', {}).get('login')
                                if reviewer == username and review.get('state') in ['APPROVED', 'CHANGES_REQUESTED']:
                                    all_reviews.append(review)
                
                page += 1
            else:
                break
        
        return len(all_reviews) * 2  # 每次review 2分
    
    # 社区贡献方法已被移除，因为当前贡献值计算中未使用


    
    def calculate_user_contribution_for_repo(self, repo: str, username: str) -> Dict[str, Any]:
        """计算单个用户在指定仓库的贡献值"""
        # 合并的PR
        repo_merged_prs = self.get_user_merged_prs(repo, username)
        merged_prs = len(repo_merged_prs)
        
        # 提出的PR
        repo_opened_prs = self.get_user_opened_prs(repo, username)
        opened_prs = len(repo_opened_prs)
        
        # 提交（排除README相关）
        repo_commits = self.get_user_commits(repo, username)
        commits = len(repo_commits)
        
        # 文档贡献（README、changelog、docs/、.md文件）
        repo_docs = self.count_documentation_contributions(repo, username)
        docs = repo_docs
        
        # 创建的issues
        repo_created_issues = self.get_user_created_issues(repo, username)
        created_issues = len(repo_created_issues)
        
        # 处理的issues（分配给用户的已关闭issues）
        repo_assigned_issues = self.get_user_assigned_issues(repo, username)
        assigned_issues = len(repo_assigned_issues)
        
        # Code Review（PR review记录）
        repo_reviews = self.get_code_quality_contributions(repo, username)
        reviews = repo_reviews
        
        # 计算总分
        total_score = (
            merged_prs * 10 +      # 合并的PR：10分
            opened_prs * 3 +       # 提出的PR：3分
            commits * 2 +          # 提交：2分
            docs * 5 +             # 文档：5分
            created_issues * 3 +   # 创建的issues：3分
            assigned_issues * 5 +  # 处理的issues：5分
            reviews * 2            # Code Review：2分
        )
        
        return {
            'total_score': total_score,
            'merged_prs': merged_prs,
            'opened_prs': opened_prs,
            'commits': commits,
            'docs': docs,
            'created_issues': created_issues,
            'assigned_issues': assigned_issues,
            'reviews': reviews
        }

    def calculate_user_contribution(self, username: str) -> Dict[str, Any]:
        """计算单个用户的总贡献值"""
        repos = ['SECTL/SecRandom', 'SECTL/SecRandom-docs']
        
        total_score = 0
        merged_prs = 0
        opened_prs = 0
        commits = 0
        docs = 0
        created_issues = 0
        assigned_issues = 0
        reviews = 0
        
        for repo in repos:
            repo_contribution = self.calculate_user_contribution_for_repo(repo, username)
            
            merged_prs += repo_contribution['merged_prs']
            opened_prs += repo_contribution['opened_prs']
            commits += repo_contribution['commits']
            docs += repo_contribution['docs']
            created_issues += repo_contribution['created_issues']
            assigned_issues += repo_contribution['assigned_issues']
            reviews += repo_contribution['reviews']
            total_score += repo_contribution['total_score']
        
        # 为了兼容控制台输出，添加repo_data字段
        repo_data = {}
        for repo in repos:
            repo_name = repo.split('/')[-1]
            repo_contribution = self.calculate_user_contribution_for_repo(repo, username)
            repo_data[repo_name] = {
                'merged_prs': repo_contribution['merged_prs'],
                'opened_prs': repo_contribution['opened_prs'],
                'commits': repo_contribution['commits'],
                'docs': repo_contribution['docs'],
                'created_issues': repo_contribution['created_issues'],
                'assigned_issues': repo_contribution['assigned_issues'],
                'reviews': repo_contribution['reviews'],
                'total_score': repo_contribution['total_score']
            }

        return {
            'username': username,
            'total_score': total_score,
            'merged_prs': merged_prs,
            'opened_prs': opened_prs,
            'commits': commits,
            'docs': docs,
            'created_issues': created_issues,
            'assigned_issues': assigned_issues,
            'reviews': reviews,
            'repo_data': repo_data
        }
    
    def get_all_contributors(self) -> List[Dict[str, Any]]:
        """获取所有贡献者并计算贡献值（带进度条）"""
        all_users = set()
        
        # 收集所有用户
        for repo in self.repos:
            contributors = self.get_repo_contributors(repo)
            for contributor in contributors:
                if contributor.get('login'):
                    all_users.add(contributor['login'])
        
        # 排除机器人用户和特定用户
        excluded_users = {'actions-user', 'github-actions[bot]', 'dependabot[bot]', 'web-flow'}
        filtered_users = all_users - excluded_users
        
        # 计算每个用户的贡献值（带进度条）
        results = []
        print("🔄 正在计算贡献者数据...")
        for username in tqdm(sorted(filtered_users), desc="处理用户", unit="用户"):
            user_data = self.calculate_user_contribution(username)
            if user_data['total_score'] > 0:  # 只包含有贡献的用户
                results.append(user_data)
        
        # 按贡献值排序
        results.sort(key=lambda x: x['total_score'], reverse=True)
        return results
    
    def generate_leaderboard_md(self) -> str:
        """生成贡献值排行榜的Markdown格式（使用tabulate优化版，限制10人，支持折叠）"""
        contributors = self.get_all_contributors()
        
        # 限制最多显示10人
        top_contributors = contributors[:10]
        
        # 使用tabulate生成总体排行榜
        headers = ["排名", "用户名", "🔀 合并PR", "📝 提出PR", "💻 Commits", "📚 文档", "🐛 创建Issue", "🔧 处理Issue", "👀 Review", "⭐ 分数"]
        table_data = []
        
        for i, contributor in enumerate(top_contributors, 1):
            table_data.append([
                f"**{i}**",
                f"**{contributor['username']}**",
                str(contributor['merged_prs']),
                str(contributor['opened_prs']),
                str(contributor['commits']),
                str(contributor['docs']),
                str(contributor['created_issues']),
                str(contributor['assigned_issues']),
                str(contributor['reviews']),
                f"**{contributor['total_score']}**"
            ])
        
        overall_table = tabulate(table_data, headers=headers, tablefmt="github")
        
        md_content = f"""### 🏆 贡献值排行榜

> 📊 **贡献值计算公式**：贡献值 = （合并PR×10分） + （提出PR×3分） + （Commits×2分） + （文档×5分） + （创建Issue×3分） + （处理Issue×5分） + （Code Review×2分）
> 
> 📅 **统计时间范围**：{self.start_date.strftime('%Y.%m.%d')} - {self.end_date.strftime('%Y.%m.%d')} (中国时间 UTC+8)
> 
> 🏗️ **统计仓库**：{', '.join(['SECTL/SecRandom', 'SECTL/SecRandom-docs'])}
> 
> ⚠️ **注意**：已排除README文件相关贡献统计和机器人用户，最多显示前10名贡献者

#### 📋 总体排行榜（前10名）

{overall_table}

---

#### 📊 各贡献者详细统计（可折叠）

"""
        
        # 添加各贡献者详细统计（支持折叠）
        for i, contributor in enumerate(top_contributors, 1):
            # 生成详细信息表格
            detail_headers = ["仓库", "🔀 合并PR", "📝 提出PR", "💻 Commits", "📚 文档", "🐛 创建Issue", "🔧 处理Issue", "👀 Review", "⭐ 分数"]
            detail_table_data = []
            
            # 分别统计两个仓库的数据
            repos = ['SECTL/SecRandom', 'SECTL/SecRandom-docs']
            for repo in repos:
                repo_name = repo.split('/')[-1]
                repo_contribution = self.calculate_user_contribution_for_repo(repo, contributor['username'])
                
                detail_table_data.append([
                    f"**{repo_name}**",
                    str(repo_contribution['merged_prs']),
                    str(repo_contribution['opened_prs']),
                    str(repo_contribution['commits']),
                    str(repo_contribution['docs']),
                    str(repo_contribution['created_issues']),
                    str(repo_contribution['assigned_issues']),
                    str(repo_contribution['reviews']),
                    f"**{repo_contribution['total_score']}**"
                ])
            
            detail_table = tabulate(detail_table_data, headers=detail_headers, tablefmt="github")
            
            # 添加折叠功能
            md_content += f"""<details>
<summary><strong>👤 第{i}名：{contributor['username']} (总分: {contributor['total_score']})</strong> - 点击展开详细统计</summary>

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
            '合并PR': contributor['merged_prs'],
            '提出PR': contributor['opened_prs'],
            '代码提交': contributor['commits'],
            '文档贡献': contributor['docs'],
            '创建Issue': contributor['created_issues'],
            '处理Issue': contributor['assigned_issues'],
            '代码审查': contributor['reviews']
        }
        
        strongest = max(contributions, key=contributions.get)
        if contributions[strongest] > 0:
            return f"{strongest} ({contributions[strongest]}次)"
        else:
            return "暂无突出贡献"
    
    def _get_main_contribution_area(self, contributor: Dict[str, Any]) -> str:
        """获取主要贡献领域"""
        # 根据不同维度的贡献判断主要领域
        if contributor['merged_prs'] > contributor['commits'] and contributor['merged_prs'] > 0:
            return "代码开发与功能实现"
        elif contributor['docs'] > 0 and contributor['docs'] >= contributor['merged_prs']:
            return "文档编写与维护"
        elif contributor['assigned_issues'] > 0 and contributor['assigned_issues'] >= contributor['created_issues']:
            return "问题处理与Bug修复"
        elif contributor['created_issues'] > 0:
            return "问题发现与反馈"
        elif contributor['reviews'] > 0:
            return "代码审查与质量把控"
        else:
            return "多方面贡献"
    
    def _get_improvement_suggestion(self, contributor: Dict[str, Any]) -> str:
        """获取改进建议"""
        suggestions = []
        
        if contributor['merged_prs'] == 0:
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
            
            # 查找插入位置（在Star历程章节之前）
            insert_marker = "## ✨ Star历程"
            if insert_marker in content:
                # 替换旧的贡献值排行榜（如果存在）
                old_leaderboard_start = "### 🏆 贡献值排行榜"
                old_leaderboard_end = "## ✨ Star历程"
                
                if old_leaderboard_start in content:
                    # 删除旧的贡献值排行榜，但保留其他章节
                    start_idx = content.find(old_leaderboard_start)
                    end_idx = content.find(old_leaderboard_end)
                    # 检查中间是否有其他章节标题（## 开头的行）
                    middle_content = content[start_idx:end_idx]
                    lines = middle_content.split('\n')
                    other_sections = []
                    in_leaderboard = True
                    
                    for line in lines:
                        if line.startswith('## ') and line != old_leaderboard_start:
                            in_leaderboard = False
                        if not in_leaderboard:
                            other_sections.append(line)
                    
                    if other_sections:
                        # 如果有其他章节，只删除贡献值排行榜部分
                        leaderboard_end_idx = start_idx + len('\n'.join(lines[:len(lines) - len(other_sections)]))
                        content = content[:start_idx] + '\n'.join(other_sections) + content[end_idx:]
                    else:
                        # 如果没有其他章节，正常删除
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
    
    headers = ["排名", "用户名", "合并PR", "提出PR", "Commit", "文档", "创建Issue", "处理Issue", "Review", "总分"]
    table_data = []
    
    # 限制控制台输出也只显示前10名
    display_contributors = contributors[:10]
    
    for i, contributor in enumerate(display_contributors, 1):
        table_data.append([
            str(i),
            contributor['username'],
            str(contributor['merged_prs']),
            str(contributor['opened_prs']),
            str(contributor['commits']),
            str(contributor['docs']),
            str(contributor['created_issues']),
            str(contributor['assigned_issues']),
            str(contributor['reviews']),

            str(contributor['total_score'])
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
        print(f"\n👤 {contributor['username']} (总分: {contributor['total_score']})")
        
        repo_headers = ["仓库", "合并PR", "提出PR", "Commit", "文档", "创建Issue", "处理Issue", "Review", "分数"]
        repo_table_data = []
        
        for repo_name, repo_data in contributor['repo_data'].items():
            repo_table_data.append([
                repo_name,
                str(repo_data['merged_prs']),
                str(repo_data['opened_prs']),
                str(repo_data['commits']),
                str(repo_data['docs']),
                str(repo_data['created_issues']),
                str(repo_data['assigned_issues']),
                str(repo_data['reviews']),

                str(repo_data['total_score'])
            ])
        
        print(tabulate(repo_table_data, headers=repo_headers, tablefmt="pretty"))
        
        # 添加个人贡献分析
        print(f"\n📈 个人贡献分析：")
        print(f"   💪 最强项：{calculator._get_strongest_contribution(contributor)}")
        print(f"   🎯 主要领域：{calculator._get_main_contribution_area(contributor)}")
        print(f"   📝 改进建议：{calculator._get_improvement_suggestion(contributor)}")
    
    print("=" * 60)
    print(f"统计时间：{calculator.start_date.strftime('%Y-%m-%d')} 至 {calculator.end_date.strftime('%Y-%m-%d')} (中国时间 UTC+8)")
    print(f"统计仓库：{', '.join(calculator.repos)}")