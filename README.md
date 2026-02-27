# 主项目README

# 🎓 办公助手Agent - 学术与职场场景智能支持系统

> 一个全能型的"数字研友"和"职场预演伙伴"

## 📌**后端因商业化规划，暂未对外开放**

## 📋 项目概述

办公助手Agent是一个智能办公助手系统，专为学生和职场人士设计，包含6个核心功能模块：

- 🎤 **会议纪要处理** - 自动处理会议音频/文字，生成结构化纪要
- 📚 **文献摘要提取** - 快速提取学术论文的核心要点
- ✍️ **学术文献润色** - 提升学术写作的规范性和表达质量
- 🌐 **多语言处理** - 支持跨语言的翻译和润色服务
- 🎨 **PPT智能生成** - 从内容自动生成专业演示文稿
- 📋 **实习周报生成** - 智能化生成周报，记录实习进度
- 🤖 **智能对话** - 自动筛选所需功能并自动执行
- 🐱‍🚀**知识库管理** - 打造你自己的私密知识库，并可以在对话中引用

## 📌部署方式
```
docker compose up -d --build
```
## 📌技术栈总览

### 后端技术栈

![1771947688534](image/TECHNICAL_ARCHITECTURE_DETAILED/1771947688534.png)

### 前端技术栈

![1771947901548](image/TECHNICAL_ARCHITECTURE_DETAILED/1771947901548.png)

### 基础设施

| 组件 | 用途 | 版本/技术 |
|-----|------|---------|
| **数据库** | 持久化存储 | PostgreSQL 12+ (异步asyncpg) |
| **缓存** | 会话状态、对话历史 | Redis 6+ |
| **搜索引擎** | 文档向量检索、全文搜索 | Elasticsearch 8.12 |
| **文件存储** | 文档、文件、媒体 | Aliyun OSS |
| **容器化** | 开发和部署 | Docker + Docker Compose |
| **反向代理** | 负载均衡、静态资源 | Nginx |

---

## 如何参与内测？
目前已经完成MVP，您如果想参与内测，欢迎填写下方问卷。
<img width="1170" height="1449" alt="内测申请" src="https://github.com/user-attachments/assets/b86634f8-e3b7-487c-a552-21605d039bfa" />

## 部署方式
```
docker compose up -d --build
```

## 🚀项目预览

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/220a2d77-7823-4bf4-a3e4-24d89b4a40f7" />


<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/508659fd-6231-4ea9-8119-b16812bf0ffb" />

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/9b60fb7a-585f-427b-8437-d2a37a2cdab4" />

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/a93e496c-ff2d-4d9f-b3d4-815c067e67ba" />

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/0e9e1518-d865-46ec-8dda-d6a9c061ab8b" />

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/65e15d08-9f1d-4dd7-ba33-00fa66d587c4" />

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/3b19e1fa-c584-4317-a289-29ee2fab390c" />

<img width="2560" height="1399" alt="image" src="https://github.com/user-attachments/assets/14677245-7f40-4b54-9022-d93063c76ddf" />

生成的PPT示例：

<img width="2475" height="1268" alt="image" src="https://github.com/user-attachments/assets/25c03245-bc97-492b-91ed-e366c35a925c" />

<img width="2475" height="1268" alt="image" src="https://github.com/user-attachments/assets/7b8255c6-59d1-41c0-8364-0e3c9476d01d" />

