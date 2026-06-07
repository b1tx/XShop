package com.example.aicommerce.product.dto;

import lombok.Data;

import javax.validation.constraints.DecimalMin;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;

@Data
public class ProductRequest {
    @NotNull
    private Long categoryId;
    @NotBlank
    private String name;
    private String subtitle;
    @NotNull
    @DecimalMin("0.01")
    private BigDecimal price;
    @NotNull
    private Integer stock;
    private String mainImage;
    private String detail;
    private Integer status;
}

