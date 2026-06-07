package com.example.aicommerce.product.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.product.dto.ProductResponse;
import com.example.aicommerce.product.service.ProductService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {
    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public ApiResponse<PageResult<ProductResponse>> page(
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "12") long size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long categoryId) {
        return ApiResponse.ok(productService.pageProducts(page, size, keyword, categoryId, 1, false));
    }

    @GetMapping("/{id}")
    public ApiResponse<ProductResponse> detail(@PathVariable Long id) {
        return ApiResponse.ok(productService.getDetail(id, false));
    }
}

