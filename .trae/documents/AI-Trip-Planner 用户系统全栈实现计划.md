# 全栈用户系统实现计划

我们将遵循前后端分离的标准开发规范，在现有项目中实现完整的用户注册、登录及鉴权系统。

## 📅 阶段一：后端架构升级与接口实现 (Backend)

目标：将单文件 `main.py` 重构为模块化架构，引入数据库 ORM 和 JWT 鉴权。

1.  **环境配置更新**
    *   在 `d:\AI-Trip-Planner\.env` 中追加数据库配置 (`DB_HOST`, `DB_USER`, `DB_PASSWORD` 等) 和 `JWT_SECRET_KEY`。
    *   创建 `backend/requirements.txt` 锁定依赖 (添加 `sqlalchemy`, `aiomysql`, `python-jose`, `passlib` 等)。

2.  **数据库层建设 (`backend/database/`)**
    *   `session.py`: 配置异步 SQLAlchemy 引擎和 SessionLocal。
    *   `models.py`: 将设计文档中的 `users`, `user_tokens`, `llm_call_logs` 映射为 ORM 模型。

3.  **核心逻辑实现 (`backend/core/` & `backend/schemas/`)**
    *   `security.py`: 实现密码哈希 (Bcrypt) 和 JWT Token 生成/解析。
    *   `schemas.py`: 定义 Pydantic 数据模型 (DTO)，用于请求参数校验和响应格式化。

4.  **路由模块化 (`backend/routers/`)**
    *   `auth.py`: 实现注册、登录、刷新 Token、退出、重置密码接口。
    *   `user.py`: 实现获取当前用户信息 (`/me`) 接口。
    *   `llm.py`: 实现 LLM 调用历史的增删查改。

5.  **入口重构 (`backend/main.py`)**
    *   引入路由 (`app.include_router`)。
    *   添加全局鉴权中间件（针对需要保护的接口）。

## 📅 阶段二：前端鉴权与页面实现 (Frontend)

目标：在 Vue3 中实现用户状态管理、登录注册页面及 API 对接。

1.  **状态管理 (`frontend/src/stores/`)**
    *   创建 `user.ts` (Pinia Store)：管理 `accessToken`, `userInfo`，实现 `login`, `logout`, `checkAuth` action。

2.  **网络层封装 (`frontend/src/utils/`)**
    *   封装 `request.ts` (Axios)：
        *   请求拦截：自动携带 Bearer Token。
        *   响应拦截：处理 401 过期，自动尝试刷新 Token 或跳转登录。

3.  **页面开发 (`frontend/src/views/auth/`)**
    *   `LoginView.vue`: 登录表单。
    *   `RegisterView.vue`: 注册表单（含验证码倒计时逻辑模拟）。
    *   `ForgotPasswordView.vue`: 忘记密码流程。

4.  **路由与守卫 (`frontend/src/router/`)**
    *   配置路由规则，添加 `meta: { requiresAuth: true }`。
    *   实现全局路由守卫：未登录访问受限页面自动跳转登录页。

5.  **UI 集成**
    *   修改 `App.vue` 或顶部导航栏：根据登录状态显示 "登录/注册" 或 "用户头像/退出"。

## 📅 阶段三：联调与验证

1.  **数据库初始化**：运行 Alembic 或脚本创建表结构。
2.  **流程测试**：
    *   新用户注册 -> 登录 -> 获取 Token -> 访问受保护接口 -> 刷新 Token -> 退出。
    *   验证 LLM 调用历史是否正确关联到当前用户。

---

**确认请求**：
该计划将对 `backend` 目录结构进行较大调整（模块化），并引入 MySQL 数据库依赖。请确认您的本地 MySQL 服务已启动，且您同意进行此架构重构。
