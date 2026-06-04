# B2C AI 电商系统开发计划

## 1. 项目概述

本项目为《面向对象技术与方法》个人结课设计，开发一个 B2C AI 电商 Web 应用。系统包含用户购物端、后台运营端、订单库存流程、限时抢购、AI 智能导购和 AI 运营助手。

技术栈：

- 后端：Spring Boot、MyBatis-Plus、Spring Security、JWT、MySQL、Redis。
- 前端：Vue3、Vite、TypeScript、Pinia、Vue Router、Axios、Element Plus、ECharts。
- AI：OpenAI 兼容 API，可接 DeepSeek、通义千问、OpenAI 或其他兼容服务。

当前本机 Java 版本为 1.8，因此首版后端采用 Spring Boot 2.7.x。若后续安装 JDK 17，可升级至 Spring Boot 3.x。

## 2. 核心功能

用户端功能：

- 注册、登录、退出登录。
- 商品首页、分类浏览、关键字搜索、商品详情。
- 购物车新增、修改数量、删除。
- 创建订单、模拟支付、取消订单、确认收货。
- AI 智能导购：商品推荐、商品对比、购买建议、商品问答。

后台端功能：

- 商品分类管理。
- 商品管理：新增、编辑、上下架、库存、价格、图片 URL。
- 订单管理：订单查询、发货、取消、状态跟踪。
- 促销管理：限时抢购活动、活动商品、活动库存。
- 用户管理：普通用户、运营管理员、系统管理员。
- 销售看板：销售额、订单数、商品销量、库存预警、近 7 日订单趋势。
- AI 运营助手：商品标题优化、商品卖点生成、销售分析、补货建议。

## 3. 后端设计

后端采用模块化单体架构，按业务边界拆分包：

- `auth`：登录、注册、JWT 认证。
- `user`：用户、角色、权限。
- `product`：商品、分类、商品图片。
- `cart`：购物车。
- `order`：订单、订单项、订单状态。
- `payment`：模拟支付记录。
- `inventory`：库存扣减、库存回滚、库存流水。
- `promotion`：限时抢购活动。
- `ai`：OpenAI 兼容 API 调用、AI 记录。
- `admin`：后台管理聚合接口。
- `dashboard`：统计看板。
- `common`：统一响应、异常处理、分页、工具类。

关键技术点：

- 使用 JWT 实现前后端分离登录。
- 使用 Spring Security 实现后台接口角色鉴权。
- 普通订单使用 MySQL 事务保证订单创建与库存扣减一致。
- 限时抢购使用 Redis 缓存活动库存，降低数据库压力。
- AI 服务调用失败时提供模板化降级结果，保证演示稳定。

## 4. 前端设计

前端采用一个 Vue3 项目承载用户端和后台端。

设计原则：

- 用户端突出商品浏览、购买路径和 AI 导购入口。
- 后台端采用操作台风格，优先展示表格、筛选、状态和数据图表。
- 保持界面克制、清晰，避免营销式大面积装饰。

页面规划：

- `/login`：登录页。
- `/register`：注册页。
- `/`：商城首页。
- `/products`：商品列表。
- `/products/:id`：商品详情。
- `/cart`：购物车。
- `/orders`：我的订单。
- `/ai-guide`：AI 智能导购。
- `/admin`：后台首页。
- `/admin/products`：商品管理。
- `/admin/orders`：订单管理。
- `/admin/promotions`：促销管理。
- `/admin/users`：用户管理。
- `/admin/dashboard`：销售看板。
- `/admin/ai-operation`：AI 运营助手。

## 5. 数据模型

主要数据表：

- `sys_user`：用户。
- `sys_role`：角色。
- `sys_user_role`：用户角色关联。
- `product_category`：商品分类。
- `product`：商品。
- `product_image`：商品图片。
- `cart_item`：购物车项。
- `order_main`：订单主表。
- `order_item`：订单明细。
- `payment_record`：支付记录。
- `inventory_record`：库存流水。
- `promotion_activity`：促销活动。
- `promotion_product`：促销商品。
- `ai_chat_record`：AI 对话记录。
- `operation_log`：操作日志。

## 6. 接口规划

核心接口：

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/profile`
- `GET /api/products`
- `GET /api/products/{id}`
- `POST /api/cart/items`
- `GET /api/cart/items`
- `PUT /api/cart/items/{id}`
- `DELETE /api/cart/items/{id}`
- `POST /api/orders`
- `POST /api/orders/{id}/pay`
- `POST /api/orders/{id}/cancel`
- `POST /api/orders/{id}/receive`
- `GET /api/admin/products`
- `POST /api/admin/products`
- `PUT /api/admin/products/{id}`
- `PUT /api/admin/products/{id}/status`
- `GET /api/admin/orders`
- `PUT /api/admin/orders/{id}/ship`
- `GET /api/admin/dashboard/overview`
- `POST /api/ai/shopping-guide`
- `POST /api/ai/product-copywriting`
- `POST /api/ai/operation-analysis`

## 7. 开发排期

2026-06-04 至 2026-06-05：

- 完成需求、数据库、接口、UML 草稿。
- 初始化 Spring Boot 后端和 Vue3 前端。
- 建立 Git 仓库和基础 README。

2026-06-06 至 2026-06-09：

- 完成登录注册、JWT、角色权限、用户管理。
- 完成商品分类、商品管理、商品列表和商品详情。
- 前端完成用户端首页、商品页、后台商品管理页。

2026-06-10 至 2026-06-13：

- 完成购物车、订单创建、订单状态、模拟支付、取消订单。
- 完成库存扣减、库存流水、后台订单管理。
- 完成主要业务链路联调。

2026-06-14 至 2026-06-16：

- 完成限时抢购、Redis 活动库存、库存预扣逻辑。
- 完成 AI 导购、商品问答、AI 商品文案、AI 运营分析。
- 完成 AI 页面和 AI 调用记录保存。

2026-06-17 至 2026-06-18：

- 完成后台销售看板、ECharts 图表、演示数据。
- 完成权限测试、订单流程测试、库存一致性测试。
- 截取运行截图。

2026-06-19 至 2026-06-20：

- 完成三份项目文档。
- 整理数据库初始化脚本、运行说明、代码量统计。
- 修复演示问题，确保项目可编译运行。

2026-06-21：

- 最终检查源码、文档、截图、数据库脚本、运行说明。
- 压缩打包并上传乐学。

## 8. 验收标准

- 能演示完整购物链路：注册登录、浏览商品、加入购物车、下单、支付、后台发货、看板变化。
- 能演示 AI 链路：用户 AI 导购推荐商品，后台 AI 生成商品文案和运营分析。
- 能演示限时抢购库存控制，避免明显超卖。
- 三份文档覆盖课程要求的 UML、架构、技术关键点、AI 使用情况和开发记录。
- 前后端总代码量不少于 10000 行。

