
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

  <sup>An intelligent office assistant designed for students and professionals, covering academic work, meetings, presentations, and more.</sup>
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

Office Assistant Agent is a versatile, all-in-one intelligent office support system. Through its modular Agent architecture, it deeply integrates academic literature processing, professional weekly reports, meeting minutes, and automated PPT generation, while also providing smart conversations and private knowledge base management. Its goal is to provide users with end-to-end efficiency support, from input to output.

> **Notice**: The backend code is currently not open-sourced due to commercialization plans. The project has completed its MVP (Minimum Viable Product) phase.

---

## Core Capabilities

- **Intelligent Dialogue** — Automatically selects required functional plugins and executes tasks.
- **Knowledge Base Management** — Build a personal, private knowledge base with RAG (Retrieval-Augmented Generation) integration in conversations.
- **Meeting Minutes Processing** — Automatically processes audio/text to generate structured meeting summaries.
- **Literature Abstract Extraction** — Quickly extracts core points and logic from academic papers.
- **Academic Text Polishing** — Enhances writing standardization and quality of academic expression.
- **AI-Powered PPT Generation** — Automatically generates professional presentations from text content.
- **Internship Weekly Report Generation** — Intelligently tracks progress and automatically produces standardized weekly reports.
- **Multi-language Support** — Provides cross-language translation and contextual polishing services.

---

## Tech Stack

### 1) System Architecture Diagram
<img width="100%" alt="Backend Tech" src="https://github.com/user-attachments/assets/9187a7c5-a2ce-4a6c-b957-9ef61f3811d1" />
<img width="100%" alt="Frontend Tech" src="https://github.com/user-attachments/assets/a503104d-73fe-42f1-becd-e8d4d362986c" />

### 2) Infrastructure Layer
| Component | Purpose | Technology/Version |
| :--- | :--- | :--- |
| **Database** | Persistent storage | PostgreSQL 12+ (with asyncpg) |
| **Cache** | Session state, conversation history | Redis 6+ |
| **Search Engine** | Document vector retrieval, full-text search | Elasticsearch 8.12 |
| **File Storage** | Documents, files, media | Aliyun OSS |
| **Containerization** | Development and deployment | Docker + Docker Compose |
| **Reverse Proxy** | Load balancing, static resources | Nginx |

---

## Deployment

Supports one-click startup of the development environment using Docker:

```bash
# Start containers after cloning the project
docker compose up -d --build
```

---

## Project Preview

### Core Functionality & PPT Example

<img width="100%" alt="Main Interface" src="https://github.com/user-attachments/assets/220a2d77-7823-4bf4-a3e4-24d89b4a40f7" />

<p align="center">
<img width="49%" src="https://github.com/user-attachments/assets/25c03245-bc97-492b-91ed-e366c35a925c" />
<img width="49%" src="https://github.com/user-attachments/assets/7b8255c6-59d1-41c0-8364-0e3c9476d01d" />
</p>

### Module Details Preview

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

The MVP development is complete. To apply for beta access, please scan the QR code or fill out the form below:

<div align="center">
<img width="60%" alt="Apply for Beta" src="https://github.com/user-attachments/assets/b86634f8-e3b7-487c-a552-21605d039bfa" />
</div>

---

## License

The backend and core Agent logic of this project are **commercial proprietary**.
Any form of code reverse engineering, copying, distribution, or commercial use without explicit authorization is strictly prohibited.

© 2024-2026 Office Assistant Agent Team. All rights reserved.
