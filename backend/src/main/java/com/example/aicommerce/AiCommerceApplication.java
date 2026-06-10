package com.example.aicommerce;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@MapperScan({
        "com.example.aicommerce.user.mapper",
        "com.example.aicommerce.product.mapper",
        "com.example.aicommerce.cart.mapper",
        "com.example.aicommerce.order.mapper",
        "com.example.aicommerce.inventory.mapper",
        "com.example.aicommerce.payment.mapper"
})
@SpringBootApplication
public class AiCommerceApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiCommerceApplication.class, args);
    }
}
