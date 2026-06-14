package com.example.aicommerce.ai.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class ProductCopywritingRequest {
    @NotBlank(message = "商品名不能为空")
    private String productName;
    private List<String> sellingPoints;
    private String targetUser;
}
