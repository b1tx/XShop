package com.example.aicommerce.product.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.product.entity.ProductCategory;
import com.example.aicommerce.product.service.CategoryService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/categories")
public class CategoryController {
    private final CategoryService categoryService;

    public CategoryController(CategoryService categoryService) {
        this.categoryService = categoryService;
    }

    @GetMapping
    public ApiResponse<List<ProductCategory>> list() {
        return ApiResponse.ok(categoryService.listEnabled());
    }
}

