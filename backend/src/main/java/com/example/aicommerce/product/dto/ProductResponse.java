package com.example.aicommerce.product.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class ProductResponse {
    private Long id;
    private Long categoryId;
    private String categoryName;
    private String name;
    private String subtitle;
    private BigDecimal price;
    private Integer stock;
    private String mainImage;
    private String detail;
    private Integer status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

