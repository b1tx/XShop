package com.example.aicommerce.promotion.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;

@Data
@TableName("promotion_product")
public class PromotionProduct {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private Long activityId;
    private Long productId;
    private BigDecimal promotionPrice;
    private Integer promotionStock;
    private Integer limitPerUser;
}
