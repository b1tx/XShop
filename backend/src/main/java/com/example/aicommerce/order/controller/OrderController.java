package com.example.aicommerce.order.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.order.dto.CreateOrderRequest;
import com.example.aicommerce.order.dto.OrderResponse;
import com.example.aicommerce.order.service.OrderService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ApiResponse<OrderResponse> create(@Validated @RequestBody CreateOrderRequest request) {
        return ApiResponse.ok(orderService.createOrder(request));
    }

    @GetMapping
    public ApiResponse<PageResult<OrderResponse>> page(
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "10") long size,
            @RequestParam(required = false) String status) {
        return ApiResponse.ok(orderService.pageCurrentUserOrders(page, size, status));
    }

    @GetMapping("/{id}")
    public ApiResponse<OrderResponse> detail(@PathVariable Long id) {
        return ApiResponse.ok(orderService.getCurrentUserOrder(id));
    }

    @PostMapping("/{id}/pay")
    public ApiResponse<OrderResponse> pay(@PathVariable Long id) {
        return ApiResponse.ok(orderService.pay(id));
    }

    @PostMapping("/{id}/cancel")
    public ApiResponse<OrderResponse> cancel(@PathVariable Long id) {
        return ApiResponse.ok(orderService.cancelCurrentUserOrder(id));
    }

    @PostMapping("/{id}/receive")
    public ApiResponse<OrderResponse> receive(@PathVariable Long id) {
        return ApiResponse.ok(orderService.receive(id));
    }
}
