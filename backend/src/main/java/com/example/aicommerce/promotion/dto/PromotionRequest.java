package com.example.aicommerce.promotion.dto;

import lombok.Data;

import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class PromotionRequest {
    @NotBlank(message = "活动名称不能为空")
    private String name;

    @NotNull(message = "开始时间不能为空")
    private LocalDateTime startTime;

    @NotNull(message = "结束时间不能为空")
    private LocalDateTime endTime;

    private Integer status;

    @Valid
    private List<PromotionProductRequest> products;
}
