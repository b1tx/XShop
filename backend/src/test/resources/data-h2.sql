INSERT INTO sys_role (id, code, name) VALUES
    (1, 'USER', '普通用户'),
    (2, 'OPERATOR', '运营管理员'),
    (3, 'ADMIN', '系统管理员');

INSERT INTO sys_user (id, username, password, nickname, phone, status) VALUES
    (1001, 'admin', '$2a$10$ht4/EgCQK1fs6WUW9Qjf6OceizPt4Og2wgXAyWb5PtF1RFHsaVTmu', '系统管理员', '13800000001', 1),
    (1002, 'operator', '$2a$10$XE43aMz31MViDZNmiUtZFeWUtILj4tdgZ24qxnY.nLO8lDafrHqii', '运营管理员', '13800000002', 1),
    (1003, 'user', '$2a$10$xoBU4OqGTbwETmQ1.cBCwOyMFQoZnQwfsP34MNtbPnxRwWpdHgTFW', '普通用户', '13800000003', 1);

INSERT INTO sys_user_role (user_id, role_id) VALUES
    (1001, 1),
    (1001, 2),
    (1001, 3),
    (1002, 2),
    (1003, 1);

INSERT INTO product_category (id, parent_id, name, sort, status) VALUES
    (2001, 0, '服饰', 10, 1),
    (2002, 0, '饰品', 20, 1);

INSERT INTO product (id, category_id, name, subtitle, price, stock, main_image, detail, status) VALUES
    (3001, 2001, '测试斗篷', '库存流程测试商品', 100.00, 20, 'https://example.com/product-3001.jpg', '用于订单流程测试', 1),
    (3002, 2002, '低库存项链', '库存不足测试商品', 50.00, 1, 'https://example.com/product-3002.jpg', '用于库存不足测试', 1);
