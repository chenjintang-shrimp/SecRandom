# 📖 GitHub 提交与贡献教程

## 🚀 快速开始

在向 SecRandom 项目贡献代码之前，请确保您已完成以下准备工作：

> 除了使用命令行，您还可以使用 GitHub Desktop 或您 IDE 中的内置功能/插件进行操作。

1. **Fork 项目**
   - 访问 [SecRandom GitHub 仓库](https://github.com/SECTL/SecRandom)
   - 点击右上角的 "Fork" 按钮创建您自己的仓库副本

2. **克隆仓库**

   ```bash
   git clone https://github.com/您的用户名/SecRandom.git
   cd SecRandom
   ```

3. **添加上游仓库**

   ```bash
   git remote add upstream https://github.com/SECTL/SecRandom.git
   ```

## 📤 提交您的贡献

1. **创建功能分支**

   ```bash
   git checkout -b feature/您的功能名称
   ```

2. **进行修改**
   - 编写您的代码
   - 添加必要的注释（请使用中文）
   - 确保遵循项目代码规范

3. **提交更改**

   ```bash
   git add .
   git commit -m "描述您的更改内容"
   ```

4. **同步上游更改**

   ```bash
   git fetch upstream
   git rebase upstream/master
   ```

5. **推送并创建 Pull Request**

   ```bash
   git push origin feature/您的功能名称
   ```

   - 访问您的 GitHub 仓库
   - 点击 "Compare & pull request" 按钮
   - 填写 PR 描述并提交

## 📋 贡献指南

### 代码规范

- 使用中文编写代码注释
- 遵循项目现有的代码风格
- 确保导入所有使用的 Qt 类，不要使用 `from spam import *` 导入。
- 验证第三方 UI 组件是否存在

> [!TIP]
> 您可以使用 **PyRight**， **Ruff** 等工具检查代码是否符合规范。

### 提交信息规范

- 使用清晰、简洁的提交信息
- 以动词开头（如：添加、修复、更新等）
- 避免过于简单的描述（如："修复bug"）

> [!TIP]
> 我们推荐使用[约定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)撰写提交信息。

### Pull Request 要求

- PR 标题应简洁明了地描述更改内容
- 提供详细的更改说明
- 确保所有测试通过
- 关联相关的 Issue（如有）
