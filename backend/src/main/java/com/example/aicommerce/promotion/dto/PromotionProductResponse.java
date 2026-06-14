package com.example.aicommerce.promotion.dto;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class PromotionProductResponse {
    private Long id;
    private Long activityId;
    private Long productId;
    private String productName;
    private String subtitle;
    private String mainImage;
    private BigDecimal originalPrice;
    private BigDecimal promotionPrice;
    private Integer promotionStock;
    private Integer remainingStock;
    private Integer limitPerUser;
}
