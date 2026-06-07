package com.example.aicommerce.product.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.product.dto.ProductRequest;
import com.example.aicommerce.product.dto.ProductResponse;
import com.example.aicommerce.product.entity.Product;

public interface ProductService extends IService<Product> {
    PageResult<ProductResponse> pageProducts(long page, long size, String keyword, Long categoryId, Integer status, boolean admin);
    ProductResponse getDetail(Long id, boolean admin);
    ProductResponse create(ProductRequest request);
    ProductResponse update(Long id, ProductRequest request);
    void updateStatus(Long id, Integer status);
}

