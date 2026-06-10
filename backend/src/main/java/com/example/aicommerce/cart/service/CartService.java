package com.example.aicommerce.cart.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.aicommerce.cart.dto.CartItemRequest;
import com.example.aicommerce.cart.dto.CartItemResponse;
import com.example.aicommerce.cart.entity.CartItem;

import java.util.List;

public interface CartService extends IService<CartItem> {
    List<CartItemResponse> listCurrentUserItems();

    CartItemResponse addItem(CartItemRequest request);

    CartItemResponse updateQuantity(Long itemId, Integer quantity);

    void deleteItem(Long itemId);
}
