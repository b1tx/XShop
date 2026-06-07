package com.example.aicommerce.product.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.product.dto.CategoryRequest;
import com.example.aicommerce.product.entity.ProductCategory;
import com.example.aicommerce.product.service.CategoryService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/admin/categories")
public class AdminCategoryController {
    private final CategoryService categoryService;

    public AdminCategoryController(CategoryService categoryService) {
        this.categoryService = categoryService;
    }

    @GetMapping
    public ApiResponse<List<ProductCategory>> list() {
        return ApiResponse.ok(categoryService.listAll());
    }

    @PostMapping
    public ApiResponse<ProductCategory> create(@Validated @RequestBody CategoryRequest request) {
        return ApiResponse.ok(categoryService.create(request));
    }

    @PutMapping("/{id}")
    public ApiResponse<ProductCategory> update(@PathVariable Long id, @Validated @RequestBody CategoryRequest request) {
        return ApiResponse.ok(categoryService.update(id, request));
    }
}

