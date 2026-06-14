# 接口设计初稿

## 1. 统一返回格式

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

分页返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "records": [],
    "total": 0,
    "page": 1,
    "size": 10
  }
}
```

## 2. 认证接口

### 注册

`POST /api/auth/register`

```json
{
  "username": "user01",
  "password": "123456",
  "nickname": "用户01",
  "phone": "13800000000"
}
```

### 登录

`POST /api/auth/login`

```json
{
  "username": "user01",
  "password": "123456"
}
```

返回：

```json
{
  "token": "jwt-token",
  "user": {
    "id": 1,
    "username": "user01",
    "roles": ["USER"]
  }
}
```

## 3. 商品接口

- `GET /api/products?page=1&size=10&keyword=&categoryId=`
- `GET /api/products/{id}`
- `GET /api/categories`

后台：

- `GET /api/admin/products`
- `POST /api/admin/products`
- `PUT /api/admin/products/{id}`
- `DELETE /api/admin/products/{id}`
- `PUT /api/admin/products/{id}/status`

## 4. 购物车接口

- `GET /api/cart/items`
- `POST /api/cart/items`
- `PUT /api/cart/items/{id}`
- `DELETE /api/cart/items/{id}`

加入购物车请求：

```json
{
  "productId": 1001,
  "quantity": 2
}
```

## 5. 订单接口

- `POST /api/orders`
- `GET /api/orders`
- `GET /api/orders/{id}`
- `POST /api/orders/{id}/pay`
- `POST /api/orders/{id}/cancel`
- `POST /api/orders/{id}/receive`

创建订单请求：

```json
{
  "cartItemIds": [1, 2],
  "receiverName": "张三",
  "receiverPhone": "13800000000",
  "receiverAddress": "北京市海淀区"
}
```

后台：

- `GET /api/admin/orders`
- `PUT /api/admin/orders/{id}/ship`

## 6. 促销接口

- `GET /api/promotions/active`
- `GET /api/promotions/{id}`
- `POST /api/promotions/{id}/orders`

后台：

- `GET /api/admin/promotions`
- `GET /api/admin/promotions/{id}`
- `POST /api/admin/promotions`
- `PUT /api/admin/promotions/{id}`
- `PUT /api/admin/promotions/{id}/status`

## 7. AI 接口

### AI 智能导购

`POST /api/ai/shopping-guide`

```json
{
  "message": "我想买一台适合学生的轻薄笔记本，预算5000左右"
}
```

### AI 商品文案

`POST /api/ai/product-copywriting`

```json
{
  "productName": "轻薄笔记本电脑",
  "sellingPoints": ["16GB内存", "长续航", "便携"],
  "targetUser": "大学生"
}
```

### AI 运营分析

`POST /api/ai/operation-analysis`

```json
{
  "dateRange": "LAST_7_DAYS",
  "focus": "库存补货建议"
}
```

### AI 商品问答

`POST /api/ai/product-qa`

```json
{
  "productId": 3001,
  "question": "这件商品适合什么场景？"
}
```

## 8. 看板接口

`GET /api/admin/dashboard/overview`

返回：

```json
{
  "salesAmount": 12800.50,
  "orderCount": 64,
  "paidOrderCount": 51,
  "lowStockCount": 8,
  "orderTrend": [],
  "topProducts": []
}
```
