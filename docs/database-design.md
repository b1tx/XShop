# 数据库设计初稿

## 1. 数据库

- 数据库类型：MySQL 8。
- 字符集：`utf8mb4`。
- 排序规则：`utf8mb4_general_ci`。
- 数据库名：`ai_commerce`。

## 2. 表清单

| 表名 | 说明 |
| --- | --- |
| `sys_user` | 用户表 |
| `sys_role` | 角色表 |
| `sys_user_role` | 用户角色关联表 |
| `product_category` | 商品分类表 |
| `product` | 商品表 |
| `product_image` | 商品图片表 |
| `cart_item` | 购物车项表 |
| `order_main` | 订单主表 |
| `order_item` | 订单明细表 |
| `payment_record` | 支付记录表 |
| `inventory_record` | 库存流水表 |
| `promotion_activity` | 促销活动表 |
| `promotion_product` | 促销商品表 |
| `ai_chat_record` | AI 对话记录表 |
| `operation_log` | 操作日志表 |

## 3. 核心字段

### `sys_user`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `username` | varchar(50) | 登录名 |
| `password` | varchar(100) | 加密密码 |
| `nickname` | varchar(50) | 昵称 |
| `phone` | varchar(20) | 手机号 |
| `status` | tinyint | 状态：1正常，0禁用 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### `product`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `category_id` | bigint | 分类 ID |
| `name` | varchar(100) | 商品名称 |
| `subtitle` | varchar(200) | 副标题 |
| `price` | decimal(10,2) | 售价 |
| `stock` | int | 库存 |
| `main_image` | varchar(255) | 主图 URL |
| `detail` | text | 商品详情 |
| `status` | tinyint | 1上架，0下架 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### `order_main`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `order_no` | varchar(40) | 订单号 |
| `user_id` | bigint | 用户 ID |
| `total_amount` | decimal(10,2) | 总金额 |
| `status` | varchar(30) | 订单状态 |
| `receiver_name` | varchar(50) | 收货人 |
| `receiver_phone` | varchar(20) | 收货电话 |
| `receiver_address` | varchar(255) | 收货地址 |
| `created_at` | datetime | 创建时间 |
| `paid_at` | datetime | 支付时间 |

订单状态：

- `CREATED`：已创建。
- `PAID`：已支付。
- `SHIPPED`：已发货。
- `RECEIVED`：已收货。
- `CANCELLED`：已取消。

### `ai_chat_record`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | bigint | 主键 |
| `user_id` | bigint | 用户 ID |
| `scene` | varchar(50) | AI 场景 |
| `prompt` | text | 用户输入 |
| `response` | text | AI 响应 |
| `model` | varchar(100) | 模型名称 |
| `created_at` | datetime | 创建时间 |

## 4. 数据一致性规则

- 创建订单时必须检查商品上架状态和库存。
- 创建订单与扣减库存放在同一数据库事务中。
- 取消未支付订单时恢复库存。
- 支付记录与订单状态变更保持一致。
- 限时抢购先扣减 Redis 活动库存，再创建订单，失败时回滚 Redis 库存。

