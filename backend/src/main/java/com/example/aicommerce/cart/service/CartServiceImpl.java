package com.example.aicommerce.cart.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.aicommerce.cart.dto.CartItemRequest;
import com.example.aicommerce.cart.dto.CartItemResponse;
import com.example.aicommerce.cart.entity.CartItem;
import com.example.aicommerce.cart.mapper.CartItemMapper;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.product.entity.Product;
import com.example.aicommerce.product.service.ProductService;
import com.example.aicommerce.security.CurrentUser;
import com.example.aicommerce.security.CurrentUserHolder;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Service
public class CartServiceImpl extends ServiceImpl<CartItemMapper, CartItem> implements CartService {
    private final ProductService productService;

    public CartServiceImpl(ProductService productService) {
        this.productService = productService;
    }

    @Override
    public List<CartItemResponse> listCurrentUserItems() {
        Long userId = CurrentUserHolder.getRequiredUser().getId();
        List<CartItem> items = list(new LambdaQueryWrapper<CartItem>()
                .eq(CartItem::getUserId, userId)
                .orderByDesc(CartItem::getCreatedAt));
        List<CartItemResponse> responses = new ArrayList<CartItemResponse>();
        for (CartItem item : items) {
            Product product = productService.getById(item.getProductId());
            if (product != null) {
                responses.add(toResponse(item, product));
            }
        }
        return responses;
    }

    @Override
    public CartItemResponse addItem(CartItemRequest request) {
        CurrentUser user = CurrentUserHolder.getRequiredUser();
        Product product = requireSaleableProduct(request.getProductId());
        CartItem item = getOne(new LambdaQueryWrapper<CartItem>()
                .eq(CartItem::getUserId, user.getId())
                .eq(CartItem::getProductId, request.getProductId()), false);
        int nextQuantity = request.getQuantity();
        if (item != null) {
            nextQuantity += item.getQuantity();
        } else {
            item = new CartItem();
            item.setUserId(user.getId());
            item.setProductId(request.getProductId());
            item.setSelected(1);
        }
        validateQuantity(product, nextQuantity);
        item.setQuantity(nextQuantity);
        saveOrUpdate(item);
        return toResponse(item, product);
    }

    @Override
    public CartItemResponse updateQuantity(Long itemId, Integer quantity) {
        if (quantity == null || quantity < 1) {
            throw new BusinessException("Quantity must be greater than 0");
        }
        CartItem item = requireOwnItem(itemId);
        Product product = requireSaleableProduct(item.getProductId());
        validateQuantity(product, quantity);
        item.setQuantity(quantity);
        updateById(item);
        return toResponse(item, product);
    }

    @Override
    public void deleteItem(Long itemId) {
        CartItem item = requireOwnItem(itemId);
        removeById(item.getId());
    }

    private CartItem requireOwnItem(Long itemId) {
        Long userId = CurrentUserHolder.getRequiredUser().getId();
        CartItem item = getById(itemId);
        if (item == null || !userId.equals(item.getUserId())) {
            throw new BusinessException("Cart item not found");
        }
        return item;
    }

    private Product requireSaleableProduct(Long productId) {
        Product product = productService.getById(productId);
        if (product == null || product.getStatus() == null || product.getStatus() != 1) {
            throw new BusinessException("Product is unavailable");
        }
        return product;
    }

    private void validateQuantity(Product product, Integer quantity) {
        if (quantity == null || quantity < 1) {
            throw new BusinessException("Quantity must be greater than 0");
        }
        if (product.getStock() == null || product.getStock() < quantity) {
            throw new BusinessException("Insufficient stock");
        }
    }

    private CartItemResponse toResponse(CartItem item, Product product) {
        CartItemResponse response = new CartItemResponse();
        response.setId(item.getId());
        response.setProductId(product.getId());
        response.setProductName(product.getName());
        response.setSubtitle(product.getSubtitle());
        response.setMainImage(product.getMainImage());
        response.setPrice(product.getPrice());
        response.setStock(product.getStock());
        response.setQuantity(item.getQuantity());
        response.setSubtotal(product.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())));
        response.setProductStatus(product.getStatus());
        return response;
    }
}
