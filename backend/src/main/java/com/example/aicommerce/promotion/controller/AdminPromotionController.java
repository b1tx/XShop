package com.example.aicommerce.promotion.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.promotion.dto.PromotionRequest;
import com.example.aicommerce.promotion.dto.PromotionResponse;
import com.example.aicommerce.promotion.service.PromotionService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/promotions")
public class AdminPromotionController {
    private final PromotionService promotionService;

    public AdminPromotionController(PromotionService promotionService) {
        this.promotionService = promotionService;
    }

    @GetMapping
    public ApiResponse<PageResult<PromotionResponse>> page(@RequestParam(defaultValue = "1") long page,
                                                           @RequestParam(defaultValue = "10") long size,
                                                           @RequestParam(required = false) String keyword,
                                                           @RequestParam(required = false) Integer status) {
        return ApiResponse.ok(promotionService.pageAdminPromotions(page, size, keyword, status));
    }

    @GetMapping("/{id}")
    public ApiResponse<PromotionResponse> detail(@PathVariable Long id) {
        return ApiResponse.ok(promotionService.getPromotion(id, true));
    }

    @PostMapping
    public ApiResponse<PromotionResponse> create(@Validated @RequestBody PromotionRequest request) {
        return ApiResponse.ok(promotionService.create(request));
    }

    @PutMapping("/{id}")
    public ApiResponse<PromotionResponse> update(@PathVariable Long id,
                                                 @Validated @RequestBody PromotionRequest request) {
        return ApiResponse.ok(promotionService.update(id, request));
    }

    @PutMapping("/{id}/status")
    public ApiResponse<Void> updateStatus(@PathVariable Long id, @RequestBody PromotionRequest request) {
        promotionService.updateStatus(id, request.getStatus());
        return ApiResponse.ok(null);
    }
}
