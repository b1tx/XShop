# B2C AI 电商系统

个人结课设计项目，技术栈为 Spring Boot + Vue3 + MySQL + Redis + OpenAI 兼容 API。

## 项目结构

```text
.
├── backend/                 # Spring Boot 后端
├── frontend/                # Vue3 前端
├── docs/                    # 计划、需求、数据库、接口、UML 草稿
└── 面向对象技术与方法结课设计.docx
```

## 当前阶段

已完成 2026-06-04 至 2026-06-05 的启动任务：

- 完成项目计划 Markdown。
- 完成需求、数据库、接口、UML 初稿。
- 初始化 Spring Boot 后端项目。
- 初始化 Vue3 前端项目。
- 建立 Git 仓库基础文件。

## 本机环境

当前机器检测到 Java 1.8、Maven 3.8.8、Node.js 20.20.0、npm 10.8.2。

后端首版使用 Spring Boot 2.7.x 以适配 Java 8；如果后续安装 JDK 17，可升级到 Spring Boot 3.x。

## 启动方式

### 后端

```bash
cd backend
mvn spring-boot:run
```

默认端口：`8080`。

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认端口：`5173`。

## 文档

- `docs/project-plan.md`：项目总体开发计划。
- `docs/requirements-draft.md`：需求文档初稿。
- `docs/database-design.md`：数据库设计初稿。
- `docs/api-design.md`：接口设计初稿。
- `docs/uml-draft.md`：UML 草稿，使用 Mermaid 表达。

