package com.example.aicommerce.ai.dto;

import lombok.Data;

import java.util.List;

@Data
public class AiResponse {
    private String scene;
    private String content;
    private String model;
    private Boolean fallback;
    private List<Long> recommendedProductIds;
}
