# XShop 哥特风电商系统

XShop 是一个基于 Spring Boot + Vue3 的 B2C 网上店铺项目。当前版本已完成用户认证、JWT 登录态、角色权限、商品分类、商品管理、用户管理，以及哥特风用户端商城首页、商品详情和后台管理页面。

## 技术栈

- 后端：Java 8、Spring Boot 2.7.18、Spring Security、JWT、MyBatis-Plus、MySQL、Redis
- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Element Plus、Axios
- 数据库：MySQL，默认库名 `ai_commerce`

## 项目结构

```text
.
├── backend/                 # Spring Boot 后端
│   └── src/main/resources/
│       ├── schema.sql       # 建表脚本
│       └── data.sql         # 初始化角色、账号、分类和商品
├── frontend/                # Vue3 前端
├── docs/                    # 需求、计划、数据库、接口和 UML 文档
└── README.md
```

## 已完成功能

- 用户注册、登录、JWT 认证、登录态持久化
- 基于角色的权限控制：`USER`、`OPERATOR`、`ADMIN`
- 首页顶部登录信息展示：游客模式、登录/注册入口、当前用户、角色、后台入口、退出登录
- 哥特风商城首页：黑色主题、轮播主视觉、简单分类、商品展示、视图大小切换
- 首页商品展示：搜索、分类筛选、紧凑/标准/大图视图、加入购物车
- 商品详情页：图片、价格、库存、详情、加入购物车
- 后台商品管理：查询、新增、编辑、上下架、删除
- 后台用户管理：分页查询、启用/禁用、角色调整
- 购物车：加入商品、修改数量、删除、结算
- 订单中心：创建订单、模拟支付、取消订单、确认收货
- 库存一致性：下单扣减库存、取消订单回滚库存、记录库存流水
- 后台订单管理：查询、筛选、查看详情、发货、取消
- 后台看板入口保留

## 角色职能

| 角色 | 名称 | 职能 |
| --- | --- | --- |
| `USER` | 普通用户 | 浏览商品、查看详情；后续用于购物车、下单、查看订单 |
| `OPERATOR` | 运营管理员 | 进入后台，管理商品、分类、上下架、库存，查看用户列表 |
| `ADMIN` | 系统管理员 | 拥有全部后台权限，包括商品管理、用户启用/禁用、用户角色调整 |

## 默认账号

导入 `data.sql` 后可使用以下账号演示：

| 账号 | 密码 | 角色 |
| --- | --- | --- |
| `admin` | `admin123` | `ADMIN`、`OPERATOR`、`USER` |
| `operator` | `operator123` | `OPERATOR` |
| `user` | `user123` | `USER` |

如果误禁用管理员账号，可在 MySQL 中执行：

```sql
UPDATE sys_user SET status = 1 WHERE username = 'admin';
```

## 数据库初始化

1. 确认本机 MySQL 已启动。
2. 修改 [backend/src/main/resources/application.yml](backend/src/main/resources/application.yml) 中的数据库用户名和密码。
3. 导入建表和初始化数据：

```bash
mysql -uroot -p --default-character-set=utf8mb4 < backend/src/main/resources/schema.sql
mysql -uroot -p --default-character-set=utf8mb4 ai_commerce < backend/src/main/resources/data.sql
```

后端默认连接：

```text
jdbc:mysql://localhost:3306/ai_commerce
```

## 启动方式

### 后端

```bash
cd backend
mvn spring-boot:run
```

默认地址：`http://localhost:8080`

构建验证：

```bash
cd backend
mvn -q -DskipTests package
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

构建验证：

```bash
cd frontend
npm run build
```

## 页面入口

- `/`：哥特风商城首页
- `/login`：登录
- `/register`：注册
- `/products/:id`：商品详情
- `/cart`：购物车
- `/orders`：我的订单
- `/orders/:id`：订单详情
- `/admin`：后台看板
- `/admin/products`：后台商品管理
- `/admin/orders`：后台订单管理
- `/admin/users`：后台用户管理

## 接口概览

### 认证

- `POST /api/auth/register`：注册普通用户
- `POST /api/auth/login`：登录并返回 JWT
- `GET /api/auth/profile`：获取当前登录用户

### 前台商品

- `GET /api/categories`：启用分类列表
- `GET /api/products`：商品分页列表，支持关键字、分类、上下架过滤
- `GET /api/products/{id}`：商品详情

### 后台管理

- `GET /api/admin/users`：分页查询用户
- `PUT /api/admin/users/{id}/status`：启用或禁用用户
- `PUT /api/admin/users/{id}/roles`：调整用户角色
- `GET /api/admin/categories`：分类列表
- `POST /api/admin/categories`：新增分类
- `PUT /api/admin/categories/{id}`：编辑分类
- `GET /api/admin/products`：后台商品列表
- `POST /api/admin/products`：新增商品
- `PUT /api/admin/products/{id}`：编辑商品
- `PUT /api/admin/products/{id}/status`：上下架商品
- `DELETE /api/admin/products/{id}`：删除商品
- `GET /api/admin/orders`：后台订单列表
- `GET /api/admin/orders/{id}`：后台订单详情
- `PUT /api/admin/orders/{id}/ship`：订单发货
- `PUT /api/admin/orders/{id}/cancel`：后台取消订单

### 购物车与订单

- `GET /api/cart/items`：当前用户购物车
- `POST /api/cart/items`：加入购物车
- `PUT /api/cart/items/{id}`：修改购物车数量
- `DELETE /api/cart/items/{id}`：删除购物车项
- `POST /api/orders`：从购物车创建订单
- `GET /api/orders`：我的订单列表
- `GET /api/orders/{id}`：订单详情
- `POST /api/orders/{id}/pay`：模拟支付
- `POST /api/orders/{id}/cancel`：取消订单
- `POST /api/orders/{id}/receive`：确认收货

## 当前阶段说明

当前已完成 2026-06-10 至 2026-06-13 阶段的核心开发内容。促销秒杀、真实 AI 接口和销售看板增强尚未实现，属于后续阶段。

商品图片当前使用远程公开图片 URL，暂未实现本地图片上传。
