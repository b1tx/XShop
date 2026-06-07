package com.example.aicommerce.product.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.aicommerce.product.dto.CategoryRequest;
import com.example.aicommerce.product.entity.ProductCategory;

import java.util.List;

public interface CategoryService extends IService<ProductCategory> {
    List<ProductCategory> listEnabled();
    List<ProductCategory> listAll();
    ProductCategory create(CategoryRequest request);
    ProductCategory update(Long id, CategoryRequest request);
}

