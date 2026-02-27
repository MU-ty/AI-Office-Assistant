
<div align="center">
  <a name="readme-top"></a>

  # AI-Office-Assistant

  <p>🎓 <strong>Academic & Career Intelligent Support System</strong> — A digital study partner and professional rehearsal companion.</p>

  **简体中文** · [English](./README.en.md)

  <p>
    <img alt="Status" src="https://img.shields.io/badge/Status-MVP--Completed-brightgreen?style=flat-square" />
    <img alt="Backend" src="https://img.shields.io/badge/Backend-Proprietary-red?style=flat-square" />
    <img alt="Frontend" src="https://img.shields.io/badge/Frontend-React%20%2F%20Next.js-blue?style=flat-square" />
    <img alt="AI" src="https://img.shields.io/badge/AI-LLM%20Agent-6f42c1?style=flat-square" />
    <img alt="Infrastructure" src="https://img.shields.io/badge/Infra-Docker%20%26%20Postgres-orange?style=flat-square" />
  </p>

  <sup>专为学生与职场人士打造的智能办公助手，涵盖学术、会议及演示文稿等全场景。</sup>
</div>

<details>
  <summary><kbd>Table of contents</kbd></summary>

  - [Overview](#overview)
  - [Core Capabilities](#core-capabilities)
  - [Tech Stack](#tech-stack)
  - [Deployment](#deployment)
  - [Project Preview](#project-preview)
  - [Beta Program](#beta-program)
  - [License](#license)
</details>

---

## Overview

办公助手Agent是一个全能型的智能办公助手系统。它通过模块化的 Agent 架构，将学术文献处理、职场周报、会议记录及 PPT 自动化生成深度集成，并提供智能对话与私密知识库管理功能，旨在为用户提供从输入到输出的全流程效率支持。

> **Notice**: 后端代码因商业化规划暂未对外开放。目前项目已完成 MVP 版本开发。

---

## Core Capabilities

- **智能对话** — 自动筛选所需功能插件并自动执行任务
- **知识库管理** — 打造个人私密知识库，支持在对话中实现 RAG 引用
- **会议纪要处理** — 自动处理音频/文字，生成结构化纪要
- **文献摘要提取** — 快速提取学术论文核心要点与逻辑
- **学术文献润色** — 提升写作规范性与学术表达质量
- **PPT 智能生成** — 从文本内容一键自动化生成专业演示文稿
- **实习周报生成** — 智能记录进度，自动化产出规范化周报
- **多语言处理** — 提供跨语言翻译及语境优化润色服务

---

## Tech Stack

### 1) 系统架构图示
<img width="100%" alt="Backend Tech" src="https://github.com/user-attachments/assets/9187a7c5-a2ce-4a6c-b957-9ef61f3811d1" />
<img width="100%" alt="Frontend Tech" src="https://github.com/user-attachments/assets/a503104d-73fe-42f1-becd-e8d4d362986c" />

### 2) 基础设施层
| 组件 | 用途 | 版本/技术 |
| :--- | :--- | :--- |
| **数据库** | 持久化存储 | PostgreSQL 12+ (异步 asyncpg) |
| **缓存** | 会话状态、对话历史 | Redis 6+ |
| **搜索引擎** | 文档向量检索、全文搜索 | Elasticsearch 8.12 |
| **文件存储** | 文档、文件、媒体 | Aliyun OSS |
| **容器化** | 开发和部署 | Docker + Docker Compose |
| **反向代理** | 负载均衡、静态资源 | Nginx |

---

## Deployment

支持使用 Docker 进行一键化开发环境启动：

```bash
# 克隆项目后启动容器
docker compose up -d --build

```

---

## Project Preview

### 核心功能与 PPT 示例

<img width="100%" alt="Main Interface" src="https://github.com/user-attachments/assets/220a2d77-7823-4bf4-a3e4-24d89b4a40f7" />

<p align="center">
<img width="49%" src="https://github.com/user-attachments/assets/25c03245-bc97-492b-91ed-e366c35a925c" />
<img width="49%" src="https://github.com/user-attachments/assets/7b8255c6-59d1-41c0-8364-0e3c9476d01d" />
</p>

### 模块细节预览

<p align="center">
<img width="32%" src="https://github.com/user-attachments/assets/9b60fb7a-585f-427b-8437-d2a37a2cdab4" />
<img width="32%" src="https://github.com/user-attachments/assets/a93e496c-ff2d-4d9f-b3d4-815c067e67ba" />
</p>
<p align="center">
<img width="32%" src="https://github.com/user-attachments/assets/0e9e1518-d865-46ec-8dda-d6a9c061ab8b" />
<img width="32%" src="https://github.com/user-attachments/assets/3b19e1fa-c584-4317-a289-29ee2fab390c" />
</p>

---

## Beta Program

目前已经完成 MVP 阶段开发。如需参与内测，请扫描或填写下方问卷：

<div align="center">
<img width="60%" alt="Apply for Beta" src="https://github.com/user-attachments/assets/b86634f8-e3b7-487c-a552-21605d039bfa" />
</div>

---

## License

本项目的后端及核心 Agent 逻辑为 **商业私有 (Proprietary)**。
未经授权禁止进行任何形式的代码逆向、复制、分发或用于商业用途。

© 2024-2026 Office Assistant Agent Team. All rights reserved.
