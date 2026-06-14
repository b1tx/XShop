package com.example.aicommerce.promotion.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.order.dto.OrderResponse;
import com.example.aicommerce.promotion.dto.PromotionOrderRequest;
import com.example.aicommerce.promotion.dto.PromotionResponse;
import com.example.aicommerce.promotion.service.PromotionService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/promotions")
public class PromotionController {
    private final PromotionService promotionService;

    public PromotionController(PromotionService promotionService) {
        this.promotionService = promotionService;
    }

    @GetMapping("/active")
    public ApiResponse<List<PromotionResponse>> active() {
        return ApiResponse.ok(promotionService.listActivePromotions());
    }

    @GetMapping("/{id}")
    public ApiResponse<PromotionResponse> detail(@PathVariable Long id) {
        return ApiResponse.ok(promotionService.getPromotion(id, false));
    }

    @PostMapping("/{id}/orders")
    public ApiResponse<OrderResponse> createOrder(@PathVariable Long id,
                                                  @Validated @RequestBody PromotionOrderRequest request) {
        return ApiResponse.ok(promotionService.createPromotionOrder(id, request));
    }
}
