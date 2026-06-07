package com.example.aicommerce.product.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.product.dto.ProductRequest;
import com.example.aicommerce.product.dto.ProductResponse;
import com.example.aicommerce.product.entity.Product;
import com.example.aicommerce.product.entity.ProductCategory;
import com.example.aicommerce.product.mapper.ProductMapper;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

@Service
public class ProductServiceImpl extends ServiceImpl<ProductMapper, Product> implements ProductService {
    private final CategoryService categoryService;

    public ProductServiceImpl(CategoryService categoryService) {
        this.categoryService = categoryService;
    }

    @Override
    public PageResult<ProductResponse> pageProducts(long page, long size, String keyword, Long categoryId, Integer status, boolean admin) {
        LambdaQueryWrapper<Product> wrapper = new LambdaQueryWrapper<Product>()
                .orderByDesc(Product::getCreatedAt);
        if (StringUtils.hasText(keyword)) {
            wrapper.and(query -> query.like(Product::getName, keyword).or().like(Product::getSubtitle, keyword));
        }
        if (categoryId != null) {
            wrapper.eq(Product::getCategoryId, categoryId);
        }
        if (admin) {
            if (status != null) {
                wrapper.eq(Product::getStatus, status);
            }
        } else {
            wrapper.eq(Product::getStatus, 1);
        }
        Page<Product> productPage = page(new Page<Product>(page, size), wrapper);
        List<ProductResponse> records = new ArrayList<ProductResponse>();
        for (Product product : productPage.getRecords()) {
            records.add(toResponse(product));
        }
        return new PageResult<ProductResponse>(records, productPage.getTotal(), productPage.getCurrent(), productPage.getSize());
    }

    @Override
    public ProductResponse getDetail(Long id, boolean admin) {
        Product product = getById(id);
        if (product == null || (!admin && (product.getStatus() == null || product.getStatus() != 1))) {
            throw new BusinessException("商品不存在或已下架");
        }
        return toResponse(product);
    }

    @Override
    public ProductResponse create(ProductRequest request) {
        validateCategory(request.getCategoryId());
        Product product = new Product();
        apply(product, request);
        save(product);
        return toResponse(product);
    }

    @Override
    public ProductResponse update(Long id, ProductRequest request) {
        Product product = getById(id);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        validateCategory(request.getCategoryId());
        apply(product, request);
        updateById(product);
        return toResponse(product);
    }

    @Override
    public void updateStatus(Long id, Integer status) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BusinessException("商品状态不正确");
        }
        Product product = getById(id);
        if (product == null) {
            throw new BusinessException("商品不存在");
        }
        product.setStatus(status);
        updateById(product);
    }

    private void validateCategory(Long categoryId) {
        if (categoryService.getById(categoryId) == null) {
            throw new BusinessException("分类不存在");
        }
    }

    private void apply(Product product, ProductRequest request) {
        product.setCategoryId(request.getCategoryId());
        product.setName(request.getName());
        product.setSubtitle(request.getSubtitle());
        product.setPrice(request.getPrice());
        product.setStock(request.getStock() == null ? 0 : request.getStock());
        product.setMainImage(request.getMainImage());
        product.setDetail(request.getDetail());
        product.setStatus(request.getStatus() == null ? 1 : request.getStatus());
    }

    private ProductResponse toResponse(Product product) {
        ProductResponse response = new ProductResponse();
        response.setId(product.getId());
        response.setCategoryId(product.getCategoryId());
        ProductCategory category = categoryService.getById(product.getCategoryId());
        response.setCategoryName(category == null ? "" : category.getName());
        response.setName(product.getName());
        response.setSubtitle(product.getSubtitle());
        response.setPrice(product.getPrice());
        response.setStock(product.getStock());
        response.setMainImage(product.getMainImage());
        response.setDetail(product.getDetail());
        response.setStatus(product.getStatus());
        response.setCreatedAt(product.getCreatedAt());
        response.setUpdatedAt(product.getUpdatedAt());
        return response;
    }
}

