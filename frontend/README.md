# Office Assistant Agent - 前端

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
npm run dev
```

服务将在 `http://localhost:3000` 启动

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/       # React组件
│   │   └── Layout.tsx    # 布局组件
│   ├── pages/            # 页面组件
│   │   ├── HomePage.tsx
│   │   └── NotFound.tsx
│   ├── services/         # API服务
│   │   └── api.ts        # API客户端配置
│   ├── store/            # 状态管理 (Zustand)
│   │   └── app.ts
│   ├── types/            # TypeScript类型定义
│   │   └── index.ts
│   ├── hooks/            # 自定义Hooks
│   │   └── useAsync.ts
│   ├── utils/            # 工具函数
│   │   └── date.ts
│   ├── App.tsx           # 根组件
│   ├── App.css
│   ├── main.tsx          # 入口文件
│   └── index.css         # 全局样式
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 技术栈

- **React 18**: UI框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **React Router**: 路由管理
- **Zustand**: 状态管理
- **Axios**: HTTP客户端
- **Material-UI**: UI组件库
- **ESLint**: 代码检查

## API配置

API请求通过 `/api` 代理到后端服务器 (`http://localhost:8000`)。

修改 `vite.config.ts` 中的 `proxy` 配置可以改变代理地址。

## 功能模块开发

### 1. 添加新页面

```typescript
// src/pages/NewPage.tsx
export default function NewPage() {
  return <div>New Page</div>
}
```

### 2. 在路由中注册

```typescript
// App.tsx
<Route path="/new" element={<NewPage />} />
```

### 3. 创建服务层

```typescript
// src/services/featureService.ts
import { apiClient } from './api'

export const getFeatureData = () => apiClient.get('/feature')
```

## 代码规范

- 使用 ESLint 检查代码质量
- 使用 TypeScript 进行类型检查
- 组件使用函数式组件
- 使用 Hooks 管理状态

## 下一步

1. 实现各功能模块的页面
2. 完成身份认证和授权
3. 添加上传文件功能
4. 实现实时通知
5. 优化性能和用户体验
