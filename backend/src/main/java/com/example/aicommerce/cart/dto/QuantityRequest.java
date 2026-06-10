package com.example.aicommerce.cart.dto;

import lombok.Data;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;

@Data
public class QuantityRequest {
    @NotNull
    @Min(1)
    private Integer quantity;
}
