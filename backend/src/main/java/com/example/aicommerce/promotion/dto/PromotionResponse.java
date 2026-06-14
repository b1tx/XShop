package com.example.aicommerce.promotion.dto;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class PromotionResponse {
    private Long id;
    private String name;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Integer status;
    private String timeStatus;
    private LocalDateTime createdAt;
    private List<PromotionProductResponse> products;
}
