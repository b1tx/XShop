package com.example.aicommerce.promotion.dto;

import lombok.Data;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

@Data
public class PromotionOrderRequest {
    @NotNull(message = "活动商品不能为空")
    private Long promotionProductId;

    @Min(value = 1, message = "购买数量必须大于 0")
    private Integer quantity = 1;

    @NotBlank(message = "收货人不能为空")
    private String receiverName;

    @NotBlank(message = "电话不能为空")
    private String receiverPhone;

    @NotBlank(message = "地址不能为空")
    private String receiverAddress;
}
