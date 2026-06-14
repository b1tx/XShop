package com.example.aicommerce.order.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.order.dto.CreateOrderRequest;
import com.example.aicommerce.order.dto.OrderResponse;
import com.example.aicommerce.order.entity.OrderMain;

import java.math.BigDecimal;

public interface OrderService extends IService<OrderMain> {
    OrderResponse createOrder(CreateOrderRequest request);

    OrderResponse createDirectOrder(Long productId,
                                    Integer quantity,
                                    BigDecimal price,
                                    Long promotionProductId,
                                    String receiverName,
                                    String receiverPhone,
                                    String receiverAddress,
                                    String businessType);

    PageResult<OrderResponse> pageCurrentUserOrders(long page, long size, String status);

    OrderResponse getCurrentUserOrder(Long id);

    OrderResponse pay(Long id);

    OrderResponse cancelCurrentUserOrder(Long id);

    OrderResponse receive(Long id);

    PageResult<OrderResponse> pageAdminOrders(long page, long size, String keyword, String status);

    OrderResponse getAdminOrder(Long id);

    OrderResponse ship(Long id);

    OrderResponse cancelAdminOrder(Long id);
}
