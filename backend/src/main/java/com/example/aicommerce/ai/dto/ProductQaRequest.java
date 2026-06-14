package com.example.aicommerce.ai.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

@Data
public class ProductQaRequest {
    @NotNull(message = "商品不能为空")
    private Long productId;

    @NotBlank(message = "请输入问题")
    private String question;
}
