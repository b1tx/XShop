package com.example.aicommerce.promotion.dto;

import lombok.Data;

import javax.validation.constraints.DecimalMin;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;

@Data
public class PromotionProductRequest {
    private Long id;

    @NotNull(message = "商品不能为空")
    private Long productId;

    @NotNull(message = "活动价不能为空")
    @DecimalMin(value = "0.01", message = "活动价必须大于 0")
    private BigDecimal promotionPrice;

    @NotNull(message = "活动库存不能为空")
    @Min(value = 0, message = "活动库存不能小于 0")
    private Integer promotionStock;

    @Min(value = 1, message = "限购数量必须大于 0")
    private Integer limitPerUser;
}
