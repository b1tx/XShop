package com.example.aicommerce.inventory.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("inventory_record")
public class InventoryRecord {
    @TableId
    private Long id;
    private Long productId;
    private Integer changeQuantity;
    private Integer beforeStock;
    private Integer afterStock;
    private String businessType;
    private Long businessId;
    private LocalDateTime createdAt;
}
