package com.example.aicommerce.ai.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class AiMessageRequest {
    @NotBlank(message = "请输入需求")
    private String message;
}
