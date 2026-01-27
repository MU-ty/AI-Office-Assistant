# API 端点完整清单

## 📋 总览

- **总端点数**: 68个
- **模块数**: 8个
- **框架完成度**: 100% ✅
- **API文档**: http://localhost:8000/api/docs

---

## 1️⃣ 用户认证模块 (8个端点)

### 基本端点
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/users/register` | 用户注册 | ❌ |
| POST | `/api/v1/users/login` | 用户登录 | ❌ |
| POST | `/api/v1/users/refresh-token` | 刷新令牌 | ❌ |
| GET | `/api/v1/users/me` | 获取当前用户信息 | ✅ |
| PUT | `/api/v1/users/me` | 更新当前用户 | ✅ |
| GET | `/api/v1/users/{user_id}` | 获取用户信息 | ✅ |
| PUT | `/api/v1/users/{user_id}` | 更新用户信息 (管理员) | ✅ |
| DELETE | `/api/v1/users/{user_id}` | 删除用户 (管理员) | ✅ |

---

## 2️⃣ 会议纪要模块 (14个端点)

### 会议管理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/meetings/` | 创建会议 | ✅ |
| GET | `/api/v1/meetings/` | 获取会议列表 | ✅ |
| GET | `/api/v1/meetings/{meeting_id}` | 获取会议详情 | ✅ |
| PUT | `/api/v1/meetings/{meeting_id}` | 更新会议 | ✅ |
| DELETE | `/api/v1/meetings/{meeting_id}` | 删除会议 | ✅ |

### 音视频处理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/meetings/{meeting_id}/upload` | 上传音视频 | ✅ |
| POST | `/api/v1/meetings/{meeting_id}/transcribe` | 触发转录 (异步) | ✅ |

### 纪要与导出
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/v1/meetings/{meeting_id}/minutes` | 获取会议纪要 | ✅ |
| POST | `/api/v1/meetings/{meeting_id}/export` | 导出纪要 | ✅ |
| POST | `/api/v1/meetings/{meeting_id}/send-email` | 发送纪要邮件 | ✅ |
| POST | `/api/v1/meetings/{meeting_id}/share` | 分享纪要 | ✅ |

### 子集合端点
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/v1/meetings/{meeting_id}/participants` | 获取参与人 | ✅ |
| GET | `/api/v1/meetings/{meeting_id}/agendas` | 获取议程 | ✅ |
| GET | `/api/v1/meetings/{meeting_id}/decisions` | 获取决议 | ✅ |
| GET | `/api/v1/meetings/{meeting_id}/action-items` | 获取Action Items | ✅ |

---

## 3️⃣ 文献摘要模块 (9个端点)

### 文档管理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/documents/` | 上传文档 | ✅ |
| GET | `/api/v1/documents/` | 获取文档列表 | ✅ |
| GET | `/api/v1/documents/{doc_id}` | 获取文档详情 | ✅ |
| PUT | `/api/v1/documents/{doc_id}` | 更新文档 | ✅ |
| DELETE | `/api/v1/documents/{doc_id}` | 删除文档 | ✅ |

### 摘要与知识提取
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/documents/{doc_id}/summarize` | 生成摘要 | ✅ |
| GET | `/api/v1/documents/{doc_id}/concepts` | 获取关键概念 | ✅ |
| GET | `/api/v1/documents/{doc_id}/citations` | 获取引用关系 | ✅ |

### 搜索
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/documents/search` | 相似文献搜索 | ✅ |

---

## 4️⃣ 学术润色模块 (9个端点)

### 任务管理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/polish/` | 创建润色任务 | ✅ |
| GET | `/api/v1/polish/` | 获取任务列表 | ✅ |
| GET | `/api/v1/polish/{task_id}` | 获取任务详情 | ✅ |
| PUT | `/api/v1/polish/{task_id}` | 更新任务 | ✅ |
| DELETE | `/api/v1/polish/{task_id}` | 删除任务 | ✅ |

### 反馈和处理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/v1/polish/{task_id}/issues` | 获取问题列表 | ✅ |
| POST | `/api/v1/polish/{task_id}/accept/{issue_id}` | 接受建议 | ✅ |
| POST | `/api/v1/polish/{task_id}/reject/{issue_id}` | 拒绝建议 | ✅ |

### 导出
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/v1/polish/{task_id}/export` | 导出结果 | ✅ |

---

## 5️⃣ 多语言翻译模块 (7个端点)

### 任务管理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/translations/` | 创建翻译任务 | ✅ |
| GET | `/api/v1/translations/` | 获取任务列表 | ✅ |
| GET | `/api/v1/translations/{task_id}` | 获取任务详情 | ✅ |
| PUT | `/api/v1/translations/{task_id}` | 更新任务 | ✅ |
| DELETE | `/api/v1/translations/{task_id}` | 删除任务 | ✅ |

### 术语库
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/v1/translations/terminology/` | 获取术语库 | ✅ |
| POST | `/api/v1/translations/terminology/add` | 添加术语 | ✅ |

### 评分
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/translations/{task_id}/rate` | 评分翻译 | ✅ |

---

## 6️⃣ PPT生成模块 (8个端点)

### 项目管理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/ppt/` | 创建PPT项目 | ✅ |
| GET | `/api/v1/ppt/` | 获取项目列表 | ✅ |
| GET | `/api/v1/ppt/{project_id}` | 获取项目详情 | ✅ |
| PUT | `/api/v1/ppt/{project_id}` | 更新项目 | ✅ |
| DELETE | `/api/v1/ppt/{project_id}` | 删除项目 | ✅ |

### 生成与导出
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/ppt/{project_id}/generate` | 生成幻灯片 | ✅ |
| GET | `/api/v1/ppt/{project_id}/slides` | 获取幻灯片列表 | ✅ |
| POST | `/api/v1/ppt/{project_id}/export` | 导出PPTX | ✅ |

---

## 7️⃣ 周报生成模块 (10个端点)

### 工作日志
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/reports/logs` | 创建工作日志 | ✅ |
| GET | `/api/v1/reports/logs` | 获取日志列表 | ✅ |

### 周报管理
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/reports/` | 生成周报 | ✅ |
| GET | `/api/v1/reports/` | 获取周报列表 | ✅ |
| GET | `/api/v1/reports/{report_id}` | 获取周报详情 | ✅ |
| PUT | `/api/v1/reports/{report_id}` | 更新周报 | ✅ |

### 审核与导出
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| POST | `/api/v1/reports/{report_id}/submit` | 提交审核 | ✅ |
| POST | `/api/v1/reports/{report_id}/review` | 审核周报 | ✅ |
| POST | `/api/v1/reports/{report_id}/export` | 导出周报 | ✅ |

---

## 8️⃣ 系统状态模块 (3个端点)

### 健康检查
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/health` | 简单健康检查 | ❌ |
| GET | `/health/detailed` | 详细健康检查 | ❌ |
| GET | `/info` | 系统信息 | ❌ |

### API文档
| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| GET | `/api/docs` | Swagger UI | ❌ |
| GET | `/api/openapi.json` | OpenAPI spec | ❌ |

---

## 🔐 认证说明

### 认证类型
- **JWT令牌**: 在 `Authorization: Bearer <token>` 中发送
- **令牌过期**: 30分钟
- **刷新令牌**: 7天有效期

### 需要认证的端点
- 所有 `/api/v1/` 的非公开端点 (除了 register/login)
- 使用 `@router.get(..., dependencies=[Depends(get_current_user)])`

### 不需要认证的端点
- `/health`
- `/health/detailed`
- `/info`
- `/api/docs`
- `/api/v1/users/register`
- `/api/v1/users/login`
- `/api/v1/users/refresh-token`

---

## 📊 端点统计

| 模块 | GET | POST | PUT | DELETE | 总计 |
|------|-----|------|-----|--------|------|
| 用户认证 | 2 | 2 | 2 | 1 | 7 |
| 会议纪要 | 8 | 3 | 1 | 1 | 13 |
| 文献摘要 | 5 | 2 | 1 | 1 | 9 |
| 学术润色 | 2 | 4 | 1 | 1 | 8 |
| 多语言翻译 | 2 | 3 | 1 | 1 | 7 |
| PPT生成 | 3 | 3 | 1 | 1 | 8 |
| 周报生成 | 4 | 4 | 1 | 0 | 9 |
| 系统状态 | 5 | 0 | 0 | 0 | 5 |
| **总计** | **31** | **21** | **8** | **6** | **66** |

---

## 🧪 测试方法

### 方法1: 使用Swagger UI
```
1. 启动应用: uvicorn app.main:app --reload
2. 打开: http://localhost:8000/api/docs
3. 点击端点展开, 输入参数, 点击"Execute"
```

### 方法2: 使用cURL
```bash
# 注册
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"123456","full_name":"Test User"}'

# 登录
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 使用令牌调用
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

### 方法3: 使用Postman
1. 导入 OpenAPI spec: `http://localhost:8000/api/openapi.json`
2. 创建环境变量: `base_url`, `token`
3. 在Postman中测试

---

## 📝 常见问题

### Q: 如何获取访问令牌?
A: 调用 `/api/v1/users/login` 获取，然后在 `Authorization: Bearer <token>` 中使用

### Q: 令牌过期了怎么办?
A: 调用 `/api/v1/users/refresh-token` 使用刷新令牌获取新的访问令牌

### Q: 如何上传大文件?
A: 
1. 使用 `multipart/form-data` 格式
2. 最大大小: 500MB (可在config中修改)
3. 支持的格式: PDF, DOCX, MP3, WAV, MP4等

### Q: 异步任务如何检查状态?
A: 任务创建后会返回 `task_id`，使用该ID查询任务详情获取状态

---

## 🔄 数据流示例

### 会议纪要流程
```
1. 创建会议: POST /api/v1/meetings/
2. 上传音频: POST /api/v1/meetings/{id}/upload
3. 触发转录: POST /api/v1/meetings/{id}/transcribe (异步)
4. 获取纪要: GET /api/v1/meetings/{id}/minutes (转录完成后)
5. 导出纪要: POST /api/v1/meetings/{id}/export
6. 发送邮件: POST /api/v1/meetings/{id}/send-email
```

### 文献处理流程
```
1. 上传文档: POST /api/v1/documents/
2. 生成摘要: POST /api/v1/documents/{id}/summarize (异步)
3. 获取概念: GET /api/v1/documents/{id}/concepts
4. 搜索相似: POST /api/v1/documents/search
```

---

**API框架完成时间**: 2026-01-24  
**所有端点**: ✅ 已定义  
**文档**: ✅ 已完成  
**下一步**: 填充业务逻辑实现

---

## 📧 邮件发送功能说明

### 接口使用
- **端点**: `POST /api/v1/meetings/{meeting_id}/send-email`
- **功能**: 发送指定会议的纪要文件到指定邮箱。

### 请求示例
```json
{
    "recipients": ["user@example.com"],
    "format": "markdown" // 可选: markdown, pdf, docx
}
```

### 文件匹配规则
系统会自动在 `uploads/` 目录下寻找符合以下命名规范的文件进行发送：
- 规则: `{meeting_id}_minutes.{后缀}`
- 示例: 
  - 请求 `meeting_id` 为 `project_alpha`，`format` 为 `pdf`
  - 系统寻找文件 `uploads/project_alpha_minutes.pdf`

此设计允许灵活发送任意已生成的纪要文件，只需确保文件名匹配即可。
