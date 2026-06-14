CREATE DATABASE IF NOT EXISTS ai_commerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE ai_commerce;

CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_sys_user_status (status),
    KEY idx_sys_user_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sys_user_role (
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    KEY idx_sys_user_role_role_id (role_id)
);

CREATE TABLE IF NOT EXISTS product_category (
    id BIGINT PRIMARY KEY,
    parent_id BIGINT DEFAULT 0,
    name VARCHAR(80) NOT NULL,
    sort INT NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_product_category_status_sort (status, sort)
);

CREATE TABLE IF NOT EXISTS product (
    id BIGINT PRIMARY KEY,
    category_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    subtitle VARCHAR(200),
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    main_image VARCHAR(255),
    detail TEXT,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_product_category_status (category_id, status),
    KEY idx_product_created_at (created_at),
    KEY idx_product_name (name)
);

CREATE TABLE IF NOT EXISTS product_image (
    id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    sort INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS cart_item (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    selected TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_cart_user_product (user_id, product_id),
    KEY idx_cart_item_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS order_main (
    id BIGINT PRIMARY KEY,
    order_no VARCHAR(40) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    receiver_name VARCHAR(50) NOT NULL,
    receiver_phone VARCHAR(20) NOT NULL,
    receiver_address VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at DATETIME NULL,
    KEY idx_order_main_user_created (user_id, created_at),
    KEY idx_order_main_status_created (status, created_at)
);

CREATE TABLE IF NOT EXISTS order_item (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    product_image VARCHAR(255),
    promotion_product_id BIGINT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    KEY idx_order_item_order_id (order_id),
    KEY idx_order_item_product_id (product_id),
    KEY idx_order_item_promotion_product_id (promotion_product_id)
);

CREATE TABLE IF NOT EXISTS payment_record (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    payment_no VARCHAR(40) NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    paid_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_payment_record_order_id (order_id)
);

CREATE TABLE IF NOT EXISTS inventory_record (
    id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    change_quantity INT NOT NULL,
    before_stock INT NOT NULL,
    after_stock INT NOT NULL,
    business_type VARCHAR(30) NOT NULL,
    business_id BIGINT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_inventory_record_product_created (product_id, created_at),
    KEY idx_inventory_record_business (business_type, business_id)
);

CREATE TABLE IF NOT EXISTS promotion_activity (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status TINYINT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_promotion_activity_status_time (status, start_time, end_time),
    KEY idx_promotion_activity_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS promotion_product (
    id BIGINT PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    promotion_price DECIMAL(10, 2) NOT NULL,
    promotion_stock INT NOT NULL,
    limit_per_user INT NOT NULL DEFAULT 1,
    KEY idx_promotion_product_activity (activity_id),
    KEY idx_promotion_product_product (product_id)
);

CREATE TABLE IF NOT EXISTS ai_chat_record (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    scene VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_ai_chat_record_user_created (user_id, created_at),
    KEY idx_ai_chat_record_scene_created (scene, created_at)
);

CREATE TABLE IF NOT EXISTS operation_log (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    module VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    detail VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
