# ai-chat-platform
基于FastAPI+Vue2的多租户AI对话平台，支持多租户数据隔离、管理员审计、软删除与30天自动清理。

AI对话平台 —— 一个面向企业的多租户AI对话解决方案。

· 多租户隔离：基于tenant_id实现用户级数据隔离，JWT鉴权保证接口安全。
· 管理员审计：管理员可查看所有租户对话记录，满足企业合规需求。
· 数据治理：软删除机制保障数据可恢复，30天自动清理过期数据。
· 流式AI对话：基于SSE实现大模型流式响应，优化交互体验。
· 技术栈：FastAPI + SQLAlchemy + JWT + Vue2 + Element UI + 大模型API

基于FastAPI+Vue2的多租户AI对话平台，接入商业大模型API，支持多用户隔离、管理员审计、数据生命周期管理。

## ✨ 核心功能

- 🏢 **多租户隔离**：基于`tenant_id`实现用户级数据隔离，每个用户只能看到自己的对话
- 🔍 **管理员审计**：管理员可查看所有租户对话记录
- ♻️ **软删除+定时清理**：用户删除为软删除，管理员可审计；30天自动清理过期数据
- ⚡ **流式AI对话**：基于Server-Sent Events实现打字机效果
- 🔐 **JWT鉴权**：自包含Token，中间件统一验证

📁 项目结构

```
aichat_backend/
├── app/
│   ├── config/       # 数据库配置
│   ├── models/       # 数据库模型
│   ├── crud/         # 增删改查逻辑
│   ├── routers/      # API路由
│   ├── schemas/      # Pydantic模型
│   └── utils/        # 工具函数
aichat_frontend/
├── src/
│   ├── api/          # 接口封装
│   ├── components/   # 公共组件
│   └── views/        # 页面
│   └── utils/        # 工具函数
│   └── store/        # VueX 状态管理
│   └── router/       # 路由
@/ai_chat.sql
├── ../               # MySQL数据库查询
```


## 🛠 技术栈

| 层级 | 技术 |
| :--- | :--- |
| 后端框架 | FastAPI |
| 数据库 | MySQL + SQLAlchemy |
| 鉴权 | JWT |
| AI集成 | 大模型API + SSE流式输出 |
| 前端 | Vue2 + Element UI |
| 部署 | Docker + Nginx |



## 🚀 快速启动

### 1. 克隆项目
```bash
git clone [你的仓库地址]
cd ai-chat-platform
```

2. 后端启动  在目录下

```bash 
pip install -r requirements.txt
# 配置.env（参考下方环境变量说明）
uvicorn app.main:app --reload
```

3. 前端启动  在目录下

```bash
npm install
npm run dev
```

4. 数据库导入依赖
```bash
任何数据库可视化软件直接执行
```

5. 配置数据库账号密码和链接端口
```bash
在后端项目里面的config/db_conf.py里面配置 数据库链接
在前端项目里面的utils/request.js里面配置 后端接口链接
```
