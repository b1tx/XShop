package com.example.aicommerce.product.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.product.dto.CategoryRequest;
import com.example.aicommerce.product.entity.ProductCategory;
import com.example.aicommerce.product.mapper.ProductCategoryMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CategoryServiceImpl extends ServiceImpl<ProductCategoryMapper, ProductCategory> implements CategoryService {

    @Override
    public List<ProductCategory> listEnabled() {
        return list(new LambdaQueryWrapper<ProductCategory>()
                .eq(ProductCategory::getStatus, 1)
                .orderByAsc(ProductCategory::getSort)
                .orderByAsc(ProductCategory::getId));
    }

    @Override
    public List<ProductCategory> listAll() {
        return list(new LambdaQueryWrapper<ProductCategory>()
                .orderByAsc(ProductCategory::getSort)
                .orderByAsc(ProductCategory::getId));
    }

    @Override
    public ProductCategory create(CategoryRequest request) {
        ProductCategory category = new ProductCategory();
        apply(category, request);
        save(category);
        return category;
    }

    @Override
    public ProductCategory update(Long id, CategoryRequest request) {
        ProductCategory category = getById(id);
        if (category == null) {
            throw new BusinessException("分类不存在");
        }
        apply(category, request);
        updateById(category);
        return category;
    }

    private void apply(ProductCategory category, CategoryRequest request) {
        category.setName(request.getName());
        category.setParentId(request.getParentId() == null ? 0L : request.getParentId());
        category.setSort(request.getSort() == null ? 0 : request.getSort());
        category.setStatus(request.getStatus() == null ? 1 : request.getStatus());
    }
}

