package com.example.aicommerce.product.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.product.dto.ProductRequest;
import com.example.aicommerce.product.dto.ProductResponse;
import com.example.aicommerce.product.service.ProductService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/products")
public class AdminProductController {
    private final ProductService productService;

    public AdminProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public ApiResponse<PageResult<ProductResponse>> page(
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "10") long size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) Integer status) {
        return ApiResponse.ok(productService.pageProducts(page, size, keyword, categoryId, status, true));
    }

    @PostMapping
    public ApiResponse<ProductResponse> create(@Validated @RequestBody ProductRequest request) {
        return ApiResponse.ok(productService.create(request));
    }

    @PutMapping("/{id}")
    public ApiResponse<ProductResponse> update(@PathVariable Long id, @Validated @RequestBody ProductRequest request) {
        return ApiResponse.ok(productService.update(id, request));
    }

    @PutMapping("/{id}/status")
    public ApiResponse<Void> updateStatus(@PathVariable Long id, @RequestBody Map<String, Integer> body) {
        productService.updateStatus(id, body.get("status"));
        return ApiResponse.ok();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        productService.removeById(id);
        return ApiResponse.ok();
    }
}

