package com.example.aicommerce.cart.controller;

import com.example.aicommerce.cart.dto.CartItemRequest;
import com.example.aicommerce.cart.dto.CartItemResponse;
import com.example.aicommerce.cart.dto.QuantityRequest;
import com.example.aicommerce.cart.service.CartService;
import com.example.aicommerce.common.ApiResponse;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cart/items")
public class CartController {
    private final CartService cartService;

    public CartController(CartService cartService) {
        this.cartService = cartService;
    }

    @GetMapping
    public ApiResponse<List<CartItemResponse>> list() {
        return ApiResponse.ok(cartService.listCurrentUserItems());
    }

    @PostMapping
    public ApiResponse<CartItemResponse> add(@Validated @RequestBody CartItemRequest request) {
        return ApiResponse.ok(cartService.addItem(request));
    }

    @PutMapping("/{id}")
    public ApiResponse<CartItemResponse> update(@PathVariable Long id, @Validated @RequestBody QuantityRequest request) {
        return ApiResponse.ok(cartService.updateQuantity(id, request.getQuantity()));
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        cartService.deleteItem(id);
        return ApiResponse.ok();
    }
}
