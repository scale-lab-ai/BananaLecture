<div align="center">

<!-- omit in toc -->

# 🍌 BananaLecture 🎙️

<img width="128" src="./assets/logo.png">

*将静态PPT转换为动态有声微课堂，让课堂更有趣*

[![Version](https://img.shields.io/badge/version-v0.3.0-4CAF50.svg?style=for-the-badge&logo=git&logoColor=white)](https://github.com/scale-lab-ai/BananaLecture)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/chengjiale150/bananalecture)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge&logo=open-source-initiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![Star](https://img.shields.io/github/stars/scale-lab-ai/BananaLecture.svg?style=for-the-badge&label=Star&maxAge=2592000&logo=github&logoColor=white)](https://github.com/scale-lab-ai/BananaLecture)

*如果该项目对你有用， 欢迎star🌟 &  fork🍴*

</div>

## 📖 目录

- [项目简介](#-项目简介)
- [功能介绍](#-功能介绍)
- [快速开始](#-快速开始)
- [故障排除](#-故障排除)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)


## ✨ 项目简介

现有课堂教学受限于传统的静态PPT单向输出的模式，导致学生注意力难以长时间维持，课堂抬头率低，教学效果大打折扣。针对上述问题，我们开发了*BananaLecture*，**<u>仅需上传PPT即可一键生成带有沉浸式多角色互动的动态有声微课堂</u>**，让课堂变得更有趣，打通沉浸式教学最后一公里。

### 🎨 结果展示

下面展示了使用哆啦A梦风格的PPT生成的带有**沉浸式音效（开场白+道具音效）**与**旁白讲解与角色互动**的动态微课堂(部分页面)。

https://github.com/user-attachments/assets/9952871a-8316-4e44-8866-780b356da414

https://github.com/user-attachments/assets/68838843-96e9-479e-bc70-6ff66795e62b

### 🚀 核心优势

- 🎭 **多角色对话**：哆啦A梦与大雄的黄金搭档，生动讲解疑难知识点
- 🔊 **沉浸式音效**：娓娓道来的旁白讲解与道具音效，提升学习沉浸感
- 🎛️ **高可控编辑**：全面支持人工编辑任意生成内容，满足个性化教学需求

<details>
<summary><b>相关竞品分析</b></summary>

比起**伪交互**、**不可控**与**黑盒化**相关竞品，我们的项目兼具“技术成熟度”与“场景可控性”，具备高度的定制性和灵活性，专注解决课堂教学实际痛点，真正做到**打通沉浸式课堂教学最后一公里**。

<img width="2000" alt="current solution" src="https://github.com/user-attachments/assets/cfd89b66-aeaa-4fe2-a4d5-2fd55e409b11" />

</details>

### 👨‍🏫 适用场景

1. **教师**：打造“哆啦A梦微课堂”作为课前引入，提升学生兴趣与吸收效果
2. **学生**：将知识点转化为视听结合的“哆啦A梦微课堂”，提升学习效率和记忆效果
3. **内容创作者**：生成哆啦A梦交互式视频，拓展知识传播渠道与效果

## 🎯 功能介绍

### 方便快捷的一键生成
- **一键生成**: 一键完成"拆分页面->生成口播稿->生成音频"全流程
- **分阶段逐步生成**: 支持分阶段进行操作，灵活定制生成过程
- **可视化进度**: 提供可视化进度条，方便跟踪生成进度
- **多样化导出格式**: 支持导出为可播放音频的PPT/MP4视频

<div align="center">
  <img width="800" src="https://github.com/user-attachments/assets/65dc7f04-2a8a-4d59-bcee-5dfc9b49adcd">
</div>

### 高度可控的编辑配置
- **页面口播稿**: 支持自定义每个对话的内容、情感、语速等参数

<div align="center">
  <img width="800" src="https://github.com/user-attachments/assets/093dbd79-5628-4bfd-acbf-94c24153605f">
</div>

- **多角色设定**: 支持自定义每个对话的角色，如哆啦A梦、大雄等

<div align="center">
  <img width="800" src="https://github.com/user-attachments/assets/e0157d38-cbd6-488b-828e-c7600099cfa0">
</div>

- **自定义音色**: 支持自定义每个角色的音色，多种音色可供选择

<div align="center">
  <img width="800" src="https://github.com/user-attachments/assets/64277de3-739f-4e98-b945-ea577273948d">
</div>

## 🏁 快速开始

1. **拉取项目代码**

```bash
git clone https://github.com/scale-lab-ai/BananaLecture.git
cd BananaLecture
```

2. **配置环境变量**

```bash
cp .env.example .env
```

从[Openrouter](https://openrouter.ai/)获取LLM API密钥并配置为`LLM_OPENAI_API_KEY`。
从[MiniMax](https://platform.minimaxi.com/)获取语音合成API密钥与Group id，并分别配置为`MINIMAX_AUDIO_API_KEY`与`MINIMAX_AUDIO_GROUP_ID`。

3. **克隆角色音色**

> [!TIP]
> 本项目对哆啦A梦进行了特殊支持，添加了极具沉浸感的开场白与道具音效
> 
> 请克隆哆啦A梦与大雄音色以获取最佳效果

<details>
<summary><b>具体克隆流程</b></summary>

> ⚠️ WARNING
> 
> 哆啦A梦与大雄的音色受版权保护，仅供学习和研究使用，请勿用于商业用途。
> 
> 克隆音色需要消耗一定的费用(9.9 RMB/音色)，请确保账户余额充足。

1. 选择任意音频源（如动画原片），分别截取10秒以上哆啦A梦与大雄的纯净音频
2. 在[Minmax音频克隆实验台](https://platform.minimaxi.com/examination-center/voice-experience-center/voiceCloning)上传待克隆音频
3. 进行音频克隆，大雄音色的voice_id命名为`bananalecture_nobita`，哆啦A梦音色的voice_id命名为`bananalecture_doraemon`
4. 启动项目在音色组别中选择`Doraemon`即可享受完整效果!

</details>


4. **启动项目**

安装[🐳 Docker](https://www.docker.com/)，使用docker-compose在<b>项目目录下</b>启动项目。

<details>
<summary>🪟 Windows用户说明</summary>

如果你使用 Windows, 请先安装 Windows Docker Desktop，检查系统托盘中的 Docker 图标，确保 Docker 正在运行，然后使用相同的步骤操作。

> **提示**：如果遇到问题，确保在 Docker Desktop 设置中启用了 WSL 2 后端（推荐），并确保端口 3574 和 8000 未被占用。

</details>

```bash
docker-compose up -d
```

成功启动后，应该会看到以下输出:

```
[+] Running 2/2
 ✔ Network bananalecture_default  Creat...            0.1s 
 ✔ Container bananalecture        Started             1.0s 
```

访问[http://localhost:3574](http://localhost:3574)即可打开前端页面，访问[http://localhost:8000/docs](http://localhost:8000/docs)即可打开后端API文档。

5. **初步测试**

在[NotebookLM](https://notebooklm.google.com/)中新建一个Notebook，上传你的资料并生成PPT，如要生成哆啦A梦风格的PPT可以使用如下提示词:

```
Create a comic in the style of Doraemon manga, depicting Doraemon teaching Nobita the core content of this document, with Chinese dialogue, in color. The comic will be used in a undergraduate class.
```

将生成的PPT(PDF格式)上传到前端页面，点击"一键生成"，静候片刻就能得到一份带生动音频的PPT了，祝你玩的开心！

## 🐛 故障排除

### 📚 常见问题

1. **脚本生成失败**
   
   - 检查OpenAI API密钥是否正确
   - 检查服务供应商是否提供tool_choice参数(要求为"required")
   - 确认网络连接正常

2. **音频生成失败**
   
   - 检查MiniMax API密钥和组ID是否正确
   - 确认账户余额充足

3. **PPT导出失败**
   
   - 确认项目已完成处理
   - 确认项目名称为英文或数字组合(不支持中文)

## 🤝 贡献指南

我们欢迎各种形式的贡献！
有关如何开始开发并提交贡献的详细说明，请参阅我们的[**贡献指南**](CONTRIBUTING.md)。

## 📄 许可证

本项目基于MIT许可证开源，您可以在遵守许可证条款的前提下自由使用、修改和分发本项目的代码。

有关详细信息，请参阅[**LICENSE**](LICENSE)文件。

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️**

Made with ❤️ by [ChengJiale](https://github.com/ChengJiale150)

</div>
