USE ai_commerce;

INSERT INTO sys_role (id, code, name) VALUES
    (1, 'USER', '普通用户'),
    (2, 'OPERATOR', '运营管理员'),
    (3, 'ADMIN', '系统管理员')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO sys_user (id, username, password, nickname, phone, status) VALUES
    (1001, 'admin', '$2a$10$ht4/EgCQK1fs6WUW9Qjf6OceizPt4Og2wgXAyWb5PtF1RFHsaVTmu', '系统管理员', '13800000001', 1),
    (1002, 'operator', '$2a$10$XE43aMz31MViDZNmiUtZFeWUtILj4tdgZ24qxnY.nLO8lDafrHqii', '运营管理员', '13800000002', 1),
    (1003, 'user', '$2a$10$xoBU4OqGTbwETmQ1.cBCwOyMFQoZnQwfsP34MNtbPnxRwWpdHgTFW', '普通用户', '13800000003', 1)
ON DUPLICATE KEY UPDATE nickname = VALUES(nickname), phone = VALUES(phone), status = VALUES(status);

INSERT INTO sys_user_role (user_id, role_id) VALUES
    (1001, 1),
    (1001, 2),
    (1001, 3),
    (1002, 2),
    (1003, 1)
ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);

INSERT INTO product_category (id, parent_id, name, sort, status) VALUES
    (2001, 0, '服饰', 10, 1),
    (2002, 0, '饰品', 20, 1),
    (2003, 0, '香氛', 30, 1),
    (2004, 0, '家居', 40, 1)
ON DUPLICATE KEY UPDATE name = VALUES(name), sort = VALUES(sort), status = VALUES(status);

INSERT INTO product (id, category_id, name, subtitle, price, stock, main_image, detail, status) VALUES
    (3001, 2001, '黑曜短斗篷外套', '重磅斜纹面料，短款廓形，适合秋冬叠穿。', 899.00, 18, 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=82', '黑色短斗篷外套，强调肩线和层次，适合晚宴、演出或日常暗色穿搭。', 1),
    (3002, 2002, '冷银月相项链', '925 银镀黑金，月相吊坠，可单戴或叠戴。', 369.00, 42, 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&w=900&q=82', '低饱和银色项链，适合作为暗色衣装的视觉中心。', 1),
    (3003, 2003, '乌木焚香香氛', '乌木、没药与微弱烟草尾调，适合夜间空间。', 259.00, 7, 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=82', '沉稳木质调香氛，适合卧室、书桌和安静的工作场景。', 1),
    (3004, 2004, '黄铜尖塔烛台', '暗金拉丝质感，适合餐桌、书柜与玄关陈列。', 439.00, 15, 'https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?auto=format&fit=crop&w=900&q=82', '黄铜色尖塔烛台，提供复古、克制的空间装饰层次。', 1),
    (3005, 2002, '黑曜石戒指套组', '三枚组合，黑曜石、刻纹银圈和窄版素圈。', 299.00, 25, 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=900&q=82', '适合叠戴的戒指套组，覆盖日常和晚宴场景。', 1),
    (3006, 2001, '暗纹丝绒手包', '细密暗纹、磁扣开合，适合晚宴和日常通勤。', 529.00, 11, 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=82', '丝绒触感手包，细节低调，容量适合日常随身物。', 1),
    (3007, 2004, '复古黑铁台灯', '低照度暖光，黑铁灯身，适合书桌与床头。', 679.00, 9, 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=82', '黑铁材质台灯，适合营造稳定、安静的阅读光线。', 1),
    (3008, 2003, '午夜玫瑰蜡烛', '玫瑰、黑胡椒与树脂气息，燃烧时间约 42 小时。', 189.00, 33, 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=82', '适合夜间空间的玫瑰调蜡烛，前调克制，尾调温暖。', 1)
ON DUPLICATE KEY UPDATE
    category_id = VALUES(category_id),
    name = VALUES(name),
    subtitle = VALUES(subtitle),
    price = VALUES(price),
    stock = VALUES(stock),
    main_image = VALUES(main_image),
    detail = VALUES(detail),
    status = VALUES(status);

