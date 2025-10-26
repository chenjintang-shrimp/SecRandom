<div align="center">

<image src="resources/secrandom-icon-paper.png" height="128"/>

# SecRandom - 公平随机抽取系统

🚀 **现代化教育工具** | 🎯 **智能权重算法** | 🎨 **优雅交互体验**

</div>

<!-- 项目状态徽章 -->
<div align="center">

[![GitHub Issues](https://img.shields.io/github/issues-search/SECTL/SecRandom?query=is%3Aopen&style=for-the-badge&color=00b4ab&logo=github&label=问题)](https://github.com/SECTL/SecRandom/issues)
[![最新版本](https://img.shields.io/github/v/release/SECTL/SecRandom?style=for-the-badge&color=00b4ab&label=最新正式版)](https://github.com/SECTL/SecRandom/releases/latest)
[![最新Beta版本](https://img.shields.io/github/v/release/SECTL/SecRandom?include_prereleases&style=for-the-badge&label=测试版)](https://github.com/SECTL/SecRandom/releases/)
[![上次更新](https://img.shields.io/github/last-commit/SECTL/SecRandom?style=for-the-badge&color=00b4ab&label=最后摸鱼时间)](https://github.com/SECTL/SecRandom/commits/master)
[![下载统计](https://img.shields.io/github/downloads/SECTL/SecRandom/total?style=for-the-badge&color=00b4ab&label=累计下载)](https://github.com/SECTL/SecRandom/releases)
[![QQ群](https://img.shields.io/badge/-QQ%E7%BE%A4%EF%BD%9C833875216-blue?style=for-the-badge&logo=QQ)](https://qm.qq.com/q/iWcfaPHn7W)
[![bilibili](https://img.shields.io/badge/-UP%E4%B8%BB%EF%BD%9C黎泽懿-%23FB7299?style=for-the-badge&logo=bilibili)](https://space.bilibili.com/520571577)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://opensource.org/licenses/GPL-3.0)

![代码贡献统计](https://repobeats.axiom.co/api/embed/7d42538bcd781370672c00b6b6ecd5282802ee3d.svg "代码贡献统计图表")

</div>

> [!note]
> 
> SecRandom 本体将基于GNU GPLv3协议开源
> 
> GNU GPLv3具有Copyleft特性，也就是说，您可以修改SecRandom的源代码，但是**必须将修改版本同样以GNU GPLv3协议开源**

## 📖 目录
- [🌟 核心亮点](#-核心亮点)
- [📥 下载](#-下载)
- [📸 软件截图](#-软件截图)
- [📖 公平抽取](#-公平抽取)
- [🙏 贡献者](#-贡献者和特别感谢)
- [💝 捐献支持](#-捐献支持)
- [📞 联系方式](#-联系方式)

## 🌟 核心亮点

### 🎯 **智能公平抽取系统**
- ✅ **动态权重算法**：基于抽取次数、小组、性别等多维度计算，确保真正的公平性
- ✅ **冷启动保护**：防止新成员权重过低，保证每个人都有平等机会
- ✅ **概率可视化**：直观展示每个成员被抽中的概率，让抽取过程透明化

### 🎨 **现代化用户体验**
- ✅ **优雅UI设计**：基于 Fluent Design 的现代化界面，支持浅色/深色主题
- ✅ **悬浮窗模式**：可随时进行抽取，不影响其他工作
- ✅ **语音播报**：抽取结果自动语音播报，支持自定义语音引擎

### 🚀 **强大功能集**
- ✅ **多种抽取模式**：单人/多人/小组/性别抽取，满足不同场景需求
- ✅ **智能历史记录**：带时间戳的详细记录，支持自动清理
- ✅ **多名单管理**：支持导入/导出名单，轻松管理不同班级/团队

### 💻 **系统兼容性**
- ✅ **全平台支持**：完美兼容 Windows 7/10/11 系统
- ✅ **多架构适配**：原生支持 x64、x86 架构
- ✅ **开机自启**：支持开机自动启动，随时可用

## 📥 下载

### 🌐 官方下载页面
- 📥 **[官方下载页面](https://secrandom.netlify.app/download)** - 获取最新稳定版本和测试版本

### 📦 下载源选择

#### 官方渠道
- **GitHub 官方源** - 官方发布渠道，海外访问较快，推荐使用
- **123云盘源** - 云盘下载，不限速，适合大文件下载

#### 国内加速镜像
- **GitHub 镜像源(ghfast.top)** - 国内加速镜像，速度快且稳定
- **GitHub 镜像源(gh-proxy.com)** - 国内加速镜像，适合网络环境特殊的用户

## 🛠️ 开发环境搭建

### 使用 uv 包管理器（推荐）

该项目现已支持使用 [uv](https://github.com/astral-sh/uv) 包管理器进行依赖管理，这是一种更快速的 Python 包管理方案。

1. 安装 uv：
   ```bash
   # 在 Windows 上使用 pip 安装
   pip install uv
   
   # 或者使用官方安装脚本
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. 克隆项目并进入项目目录：
   ```bash
   git clone https://github.com/SECTL/SecRandom.git
   cd SecRandom
   ```

3. 安装依赖：
   ```bash
   uv sync
   ```

4. 运行程序：
   ```bash
   uv run python main.py
   ```

### 传统方式安装依赖

如果你不想使用 uv，也可以继续使用传统的 pip 方式安装依赖：

```bash
pip install -r requirements.txt
```

## 📸 软件截图(v1.1.0.1)
<details>
<summary>📸 软件截图展示 ✨</summary>

![点名界面](ScreenSots/主界面_抽人_浅色.png)
![抽奖界面](ScreenSots/主界面_抽奖_浅色.png)
![历史记录](ScreenSots/主界面_抽人历史记录_浅色.png)
![设置界面](ScreenSots/设置_抽人设置_浅色.png)

</details>

## 📖 公平抽取

> [!note]
>
> **简介**:
> 公平抽取是一种随机抽取方式，它确保每个成员被抽取的权重由系统决定，从而避免不公平的结果。
> 这种方式适用于需要随机且公平的抽取学生回答问题或进行其他需要公平分配的场景。
> SecRandom的公平抽取的实现基于动态权重系统，通过多个方面来进行权重的计算。

### **动态权重系统**
> [!note]
>
> 动态权重是SecRandom的公平抽取的核心机制。
> 它通过以下几个方面来计算每个成员的权重：
> 1. **总抽取次数**：被抽中次数越多权重越低，避免重复抽取
> 2. **抽取各小组次数**：平衡不同小组的抽取机会
> 3. **抽取各性别次数**：确保性别平衡
> 4. **基础权重**：可自定义的初始权重设置
> 5. **冷启动保护**：防止新成员权重过低，保证公平性

## 构建与打包

### 触发构建
在提交信息中包含 `进行打包` 即可触发自动构建流程。

```
