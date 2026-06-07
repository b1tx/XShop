package com.example.aicommerce.product.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class CategoryRequest {
    @NotBlank
    private String name;
    private Long parentId;
    private Integer sort;
    private Integer status;
}

