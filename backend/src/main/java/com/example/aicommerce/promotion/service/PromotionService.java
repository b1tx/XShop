package com.example.aicommerce.promotion.service;

import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.order.dto.OrderResponse;
import com.example.aicommerce.promotion.dto.PromotionOrderRequest;
import com.example.aicommerce.promotion.dto.PromotionRequest;
import com.example.aicommerce.promotion.dto.PromotionResponse;

import java.util.List;

public interface PromotionService {
    List<PromotionResponse> listActivePromotions();

    PromotionResponse getPromotion(Long id, boolean admin);

    PageResult<PromotionResponse> pageAdminPromotions(long page, long size, String keyword, Integer status);

    PromotionResponse create(PromotionRequest request);

    PromotionResponse update(Long id, PromotionRequest request);

    void updateStatus(Long id, Integer status);

    OrderResponse createPromotionOrder(Long activityId, PromotionOrderRequest request);
}
