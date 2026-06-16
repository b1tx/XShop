# XShop 哥特风电商系统

XShop 是一个基于 `Spring Boot 2.7.18 + Vue 3` 的 B2C 网上店铺项目。当前版本已经完成用户认证、角色权限、商品管理、购物车、订单、库存流水、限时抢购、AI 导购/问答/运营助手、商品图片上传到阿里云 OSS，以及前台哥特风购物界面统一。

## 技术栈

- 后端：Java 8、Spring Boot 2.7.18、Spring Security、JWT、MyBatis-Plus、MySQL、Redis、H2 测试库
- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Element Plus、Axios、Playwright
- 存储：MySQL 默认库名 `ai_commerce`，商品图片通过阿里云 OSS 保存访问 URL

## 项目结构

```text
.
├── backend/                 # Spring Boot 后端
│   └── src/main/resources/
│       ├── application.yml  # 公共配置，敏感项读取环境变量或 application-dev.yml
│       ├── schema.sql       # 建表脚本
│       └── data.sql         # 初始化角色、账号、分类、商品、促销数据
├── frontend/                # Vue 3 前端
├── docs/screenshots/        # 自动化运行截图
└── README.md
```

## 已完成功能

- 用户注册、登录、JWT 认证、登录态持久化。
- 角色权限控制：`USER`、`OPERATOR`、`ADMIN`。
- 前台品牌已统一为 `XSHOP`。
- 前台购物页面统一为哥特风色系：黑色、炭灰、深红、暗金、银灰、象牙灰；购物页不再使用蓝色和刺眼纯白控件。
- 首页展示登录状态栏：游客显示登录/注册，已登录显示用户、角色、退出登录；普通用户不显示后台入口。
- 首页商品展示：搜索、简单分类、视图大小切换、加入购物车、商品详情跳转。
- 限时抢购：首页可折叠抢购卡片、活动价、库存、倒计时、抢购下单。
- AI 导购：前台浮动弹窗，支持购物建议生成。
- 商品详情：图片、价格、库存、详情、加入购物车、AI 商品问答。
- 购物车：加入商品、修改数量、删除、选中结算、创建订单。
- 订单中心：支付、取消、确认收货、订单详情。
- 库存一致性：下单扣减库存，取消订单回滚库存，并写入库存流水。
- 后台商品管理：查询、新增、编辑、上下架、删除。
- 后台商品图片上传：从本地选择图片，经后端上传到阿里云 OSS，数据库保存最终图片 URL。
- 后台用户管理：分页查询、启用/禁用、角色调整。
- 后台订单管理：查询、筛选、详情、发货、取消。
- 后台促销管理：活动查询、新增/编辑、启用/停用、活动商品配置。
- 后台 AI 运营助手：商品文案生成、运营分析。
- 后端集成测试：权限、订单流程、库存一致性。
- 前端截图脚本：自动截取首页、详情、购物车、订单、后台管理页面。

## 角色职能

| 角色 | 名称 | 职能 |
| --- | --- | --- |
| `USER` | 普通用户 | 浏览商品、查看详情、使用购物车、下单、支付、取消、确认收货、查看自己的订单 |
| `OPERATOR` | 运营管理员 | 进入后台，管理商品、分类、订单、促销活动，使用 AI 运营助手 |
| `ADMIN` | 系统管理员 | 拥有全部后台权限，包括用户启用/禁用、角色调整，以及所有运营管理能力 |

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
2. 创建或确认数据库 `ai_commerce` 存在。
3. 导入建表和初始化数据：

```bash
mysql -uroot -p --default-character-set=utf8mb4 < backend/src/main/resources/schema.sql
mysql -uroot -p --default-character-set=utf8mb4 ai_commerce < backend/src/main/resources/data.sql
```

旧库增量升级到限时抢购订单时，需要补充字段：

```sql
ALTER TABLE order_item ADD COLUMN promotion_product_id BIGINT NULL AFTER product_image;
ALTER TABLE order_item ADD KEY idx_order_item_promotion_product_id (promotion_product_id);
```

后端默认 JDBC URL 已包含 `allowPublicKeyRetrieval=true`，用于兼容 MySQL 8 常见连接问题。

## 本地配置

公共配置位于 `backend/src/main/resources/application.yml`。数据库、Redis、OSS、AI 等敏感配置应通过环境变量或本地 `application-dev.yml` 提供。

`application-dev.yml` 已加入 `.gitignore`，不要提交真实数据库密码、OSS AccessKey 或 AI API Key。

可用配置项示例：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/ai_commerce?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
    username: root
    password: your-password
  redis:
    host: localhost
    port: 6379

aliyun:
  oss:
    endpoint: oss-cn-beijing.aliyuncs.com
    bucket-name: your-bucket
    access-key-id: your-access-key-id
    access-key-secret: your-access-key-secret
    public-base-url: https://your-bucket.oss-cn-beijing.aliyuncs.com

ai:
  openai-compatible:
    api-key: your-ai-api-key
    model: gpt-4o-mini
```

也可以使用环境变量：

```bash
DB_URL=jdbc:mysql://localhost:3306/ai_commerce?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
DB_USERNAME=root
DB_PASSWORD=your-password
REDIS_HOST=localhost
REDIS_PORT=6379
ALIYUN_OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
ALIYUN_OSS_BUCKET=your-bucket
ALIYUN_OSS_ACCESS_KEY_ID=your-access-key-id
ALIYUN_OSS_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_PUBLIC_BASE_URL=https://your-bucket.oss-cn-beijing.aliyuncs.com
AI_API_KEY=your-ai-api-key
```

## 启动方式

后端：

```bash
cd backend
mvn spring-boot:run
```

默认地址：`http://localhost:8080`

前端：

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

## 构建与测试

后端集成测试覆盖权限、订单流程、库存一致性，使用 H2 内存数据库，不依赖本机 MySQL、Redis 或 OSS：

```bash
cd backend
mvn test
```

后端打包：

```bash
cd backend
mvn -q -DskipTests package
```

前端构建：

```bash
cd frontend
npm run build
```

## 运行截图

截图脚本默认要求后端 `http://localhost:8080` 和前端 `http://127.0.0.1:5173` 已启动：

```bash
cd frontend
npm run screenshots
```

截图输出到 `docs/screenshots/`，包括：

- `store-home.png`
- `product-detail.png`
- `cart.png`
- `orders.png`
- `admin-products.png`
- `admin-orders.png`
- `admin-promotions.png`
- `admin-ai-operation.png`

## 页面入口

- `/`：XSHOP 哥特风店铺首页，包含商品展示、限时抢购、AI 导购入口
- `/login`：登录
- `/register`：注册
- `/products/:id`：商品详情
- `/cart`：购物车
- `/orders`：我的订单
- `/orders/:id`：订单详情
- `/admin`：后台看板入口
- `/admin/products`：后台商品管理
- `/admin/orders`：后台订单管理
- `/admin/promotions`：后台促销管理
- `/admin/ai-operation`：AI 运营助手
- `/admin/users`：后台用户管理

前台不再提供独立 `/products` 商品列表页，商品展示统一回到首页 `/`；`/products/:id` 商品详情页保留。

## 接口概览

### 认证

- `POST /api/auth/register`：注册普通用户
- `POST /api/auth/login`：登录并返回 JWT
- `GET /api/auth/profile`：获取当前登录用户

### 前台商品

- `GET /api/categories`：启用分类列表
- `GET /api/products`：商品分页列表，支持关键字、分类、上下架过滤
- `GET /api/products/{id}`：商品详情

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

### 促销与 AI

- `GET /api/promotions/active`：当前有效促销活动
- `GET /api/promotions/{id}`：促销活动详情
- `POST /api/promotions/{id}/orders`：创建抢购订单
- `POST /api/ai/shopping-guide`：AI 导购
- `POST /api/ai/product-qa`：AI 商品问答
- `POST /api/ai/product-copywriting`：AI 商品文案
- `POST /api/ai/operation-analysis`：AI 运营分析

### 后台管理

- `GET /api/admin/users`：分页查询用户
- `PUT /api/admin/users/{id}/status`：启用或禁用用户
- `PUT /api/admin/users/{id}/roles`：调整用户角色
- `GET /api/admin/categories`：分类列表
- `POST /api/admin/categories`：新增分类
- `PUT /api/admin/categories/{id}`：编辑分类
- `GET /api/admin/products`：后台商品列表
- `POST /api/admin/uploads/product-images`：后台商品主图上传到阿里云 OSS
- `POST /api/admin/products`：新增商品
- `PUT /api/admin/products/{id}`：编辑商品
- `PUT /api/admin/products/{id}/status`：上下架商品
- `DELETE /api/admin/products/{id}`：删除商品
- `GET /api/admin/orders`：后台订单列表
- `GET /api/admin/orders/{id}`：后台订单详情
- `PUT /api/admin/orders/{id}/ship`：订单发货
- `PUT /api/admin/orders/{id}/cancel`：后台取消订单
- `GET /api/admin/promotions`：后台促销活动列表
- `POST /api/admin/promotions`：新增促销活动
- `PUT /api/admin/promotions/{id}`：编辑促销活动
- `PUT /api/admin/promotions/{id}/status`：启用或停用促销活动

## 当前阶段说明

当前已补齐 2026-06-17 至 2026-06-18 阶段的测试、截图和运行资料能力，并完成商品图片 OSS 上传与前台购物界面哥特色系统统一。销售看板增强和更复杂的数据可视化可作为后续扩展。
