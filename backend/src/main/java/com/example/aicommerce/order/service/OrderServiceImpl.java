package com.example.aicommerce.order.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.aicommerce.cart.entity.CartItem;
import com.example.aicommerce.cart.service.CartService;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.inventory.entity.InventoryRecord;
import com.example.aicommerce.inventory.mapper.InventoryRecordMapper;
import com.example.aicommerce.order.dto.CreateOrderRequest;
import com.example.aicommerce.order.dto.OrderItemResponse;
import com.example.aicommerce.order.dto.OrderResponse;
import com.example.aicommerce.order.entity.OrderItem;
import com.example.aicommerce.order.entity.OrderMain;
import com.example.aicommerce.order.mapper.OrderItemMapper;
import com.example.aicommerce.order.mapper.OrderMainMapper;
import com.example.aicommerce.payment.entity.PaymentRecord;
import com.example.aicommerce.payment.mapper.PaymentRecordMapper;
import com.example.aicommerce.product.entity.Product;
import com.example.aicommerce.product.mapper.ProductMapper;
import com.example.aicommerce.product.service.ProductService;
import com.example.aicommerce.security.CurrentUserHolder;
import com.example.aicommerce.user.entity.SysUser;
import com.example.aicommerce.user.service.UserService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

@Service
public class OrderServiceImpl extends ServiceImpl<OrderMainMapper, OrderMain> implements OrderService {
    private static final String CREATED = "CREATED";
    private static final String PAID = "PAID";
    private static final String SHIPPED = "SHIPPED";
    private static final String RECEIVED = "RECEIVED";
    private static final String CANCELLED = "CANCELLED";

    private final CartService cartService;
    private final ProductService productService;
    private final ProductMapper productMapper;
    private final OrderItemMapper orderItemMapper;
    private final PaymentRecordMapper paymentRecordMapper;
    private final InventoryRecordMapper inventoryRecordMapper;
    private final UserService userService;

    public OrderServiceImpl(CartService cartService,
                            ProductService productService,
                            ProductMapper productMapper,
                            OrderItemMapper orderItemMapper,
                            PaymentRecordMapper paymentRecordMapper,
                            InventoryRecordMapper inventoryRecordMapper,
                            UserService userService) {
        this.cartService = cartService;
        this.productService = productService;
        this.productMapper = productMapper;
        this.orderItemMapper = orderItemMapper;
        this.paymentRecordMapper = paymentRecordMapper;
        this.inventoryRecordMapper = inventoryRecordMapper;
        this.userService = userService;
    }

    @Override
    @Transactional
    public OrderResponse createOrder(CreateOrderRequest request) {
        Long userId = CurrentUserHolder.getRequiredUser().getId();
        if (request.getCartItemIds() == null || request.getCartItemIds().isEmpty()) {
            throw new BusinessException("Cart items are required");
        }

        List<CartItem> cartItems = cartService.list(new LambdaQueryWrapper<CartItem>()
                .eq(CartItem::getUserId, userId)
                .in(CartItem::getId, request.getCartItemIds()));
        if (cartItems.size() != request.getCartItemIds().size()) {
            throw new BusinessException("Some cart items are invalid");
        }

        List<OrderItem> orderItems = new ArrayList<OrderItem>();
        BigDecimal totalAmount = BigDecimal.ZERO;

        OrderMain order = new OrderMain();
        order.setOrderNo(generateOrderNo());
        order.setUserId(userId);
        order.setStatus(CREATED);
        order.setReceiverName(request.getReceiverName());
        order.setReceiverPhone(request.getReceiverPhone());
        order.setReceiverAddress(request.getReceiverAddress());
        order.setTotalAmount(BigDecimal.ZERO);
        save(order);

        for (CartItem cartItem : cartItems) {
            Product product = productService.getById(cartItem.getProductId());
            if (product == null || product.getStatus() == null || product.getStatus() != 1) {
                throw new BusinessException("Product is unavailable");
            }
            if (cartItem.getQuantity() == null || cartItem.getQuantity() < 1) {
                throw new BusinessException("Invalid cart quantity");
            }
            int beforeStock = product.getStock() == null ? 0 : product.getStock();
            if (beforeStock < cartItem.getQuantity()) {
                throw new BusinessException("Insufficient stock: " + product.getName());
            }
            int updated = productMapper.deductStock(product.getId(), cartItem.getQuantity());
            if (updated != 1) {
                throw new BusinessException("Insufficient stock: " + product.getName());
            }

            BigDecimal itemTotal = product.getPrice().multiply(BigDecimal.valueOf(cartItem.getQuantity()));
            OrderItem orderItem = new OrderItem();
            orderItem.setOrderId(order.getId());
            orderItem.setProductId(product.getId());
            orderItem.setProductName(product.getName());
            orderItem.setProductImage(product.getMainImage());
            orderItem.setPrice(product.getPrice());
            orderItem.setQuantity(cartItem.getQuantity());
            orderItem.setTotalAmount(itemTotal);
            orderItemMapper.insert(orderItem);
            orderItems.add(orderItem);

            writeInventory(product.getId(), -cartItem.getQuantity(), beforeStock, beforeStock - cartItem.getQuantity(), "ORDER_CREATE", order.getId());
            totalAmount = totalAmount.add(itemTotal);
        }

        order.setTotalAmount(totalAmount);
        updateById(order);
        cartService.removeByIds(request.getCartItemIds());
        return toResponse(order, orderItems, true);
    }

    @Override
    public PageResult<OrderResponse> pageCurrentUserOrders(long page, long size, String status) {
        Long userId = CurrentUserHolder.getRequiredUser().getId();
        LambdaQueryWrapper<OrderMain> wrapper = new LambdaQueryWrapper<OrderMain>()
                .eq(OrderMain::getUserId, userId)
                .orderByDesc(OrderMain::getCreatedAt);
        if (StringUtils.hasText(status)) {
            wrapper.eq(OrderMain::getStatus, status);
        }
        return toPageResult(page(new Page<OrderMain>(page, size), wrapper), false);
    }

    @Override
    public OrderResponse getCurrentUserOrder(Long id) {
        OrderMain order = requireOrder(id);
        Long userId = CurrentUserHolder.getRequiredUser().getId();
        if (!userId.equals(order.getUserId())) {
            throw new BusinessException("Order not found");
        }
        return toResponse(order, loadItems(order.getId()), false);
    }

    @Override
    @Transactional
    public OrderResponse pay(Long id) {
        OrderMain order = requireCurrentUserOrder(id);
        if (!CREATED.equals(order.getStatus())) {
            throw new BusinessException("Only created orders can be paid");
        }
        LocalDateTime now = LocalDateTime.now();
        PaymentRecord payment = new PaymentRecord();
        payment.setOrderId(order.getId());
        payment.setPaymentNo("PAY" + order.getOrderNo());
        payment.setAmount(order.getTotalAmount());
        payment.setStatus("SUCCESS");
        payment.setPaidAt(now);
        paymentRecordMapper.insert(payment);

        order.setStatus(PAID);
        order.setPaidAt(now);
        updateById(order);
        return toResponse(order, loadItems(order.getId()), false);
    }

    @Override
    @Transactional
    public OrderResponse cancelCurrentUserOrder(Long id) {
        OrderMain order = requireCurrentUserOrder(id);
        return cancelOrder(order);
    }

    @Override
    public OrderResponse receive(Long id) {
        OrderMain order = requireCurrentUserOrder(id);
        if (!SHIPPED.equals(order.getStatus())) {
            throw new BusinessException("Only shipped orders can be received");
        }
        order.setStatus(RECEIVED);
        updateById(order);
        return toResponse(order, loadItems(order.getId()), false);
    }

    @Override
    public PageResult<OrderResponse> pageAdminOrders(long page, long size, String keyword, String status) {
        LambdaQueryWrapper<OrderMain> wrapper = new LambdaQueryWrapper<OrderMain>()
                .orderByDesc(OrderMain::getCreatedAt);
        if (StringUtils.hasText(status)) {
            wrapper.eq(OrderMain::getStatus, status);
        }
        if (StringUtils.hasText(keyword)) {
            wrapper.and(query -> query.like(OrderMain::getOrderNo, keyword)
                    .or().like(OrderMain::getReceiverName, keyword)
                    .or().like(OrderMain::getReceiverPhone, keyword));
        }
        return toPageResult(page(new Page<OrderMain>(page, size), wrapper), true);
    }

    @Override
    public OrderResponse getAdminOrder(Long id) {
        OrderMain order = requireOrder(id);
        return toResponse(order, loadItems(order.getId()), true);
    }

    @Override
    public OrderResponse ship(Long id) {
        OrderMain order = requireOrder(id);
        if (!PAID.equals(order.getStatus())) {
            throw new BusinessException("Only paid orders can be shipped");
        }
        order.setStatus(SHIPPED);
        updateById(order);
        return toResponse(order, loadItems(order.getId()), true);
    }

    @Override
    @Transactional
    public OrderResponse cancelAdminOrder(Long id) {
        return cancelOrder(requireOrder(id));
    }

    private OrderResponse cancelOrder(OrderMain order) {
        if (!CREATED.equals(order.getStatus()) && !PAID.equals(order.getStatus())) {
            throw new BusinessException("Only unshipped orders can be cancelled");
        }
        List<OrderItem> items = loadItems(order.getId());
        for (OrderItem item : items) {
            Product product = productService.getById(item.getProductId());
            int beforeStock = product == null || product.getStock() == null ? 0 : product.getStock();
            productMapper.restoreStock(item.getProductId(), item.getQuantity());
            writeInventory(item.getProductId(), item.getQuantity(), beforeStock, beforeStock + item.getQuantity(), "ORDER_CANCEL", order.getId());
        }
        order.setStatus(CANCELLED);
        updateById(order);
        return toResponse(order, items, true);
    }

    private OrderMain requireCurrentUserOrder(Long id) {
        OrderMain order = requireOrder(id);
        Long userId = CurrentUserHolder.getRequiredUser().getId();
        if (!userId.equals(order.getUserId())) {
            throw new BusinessException("Order not found");
        }
        return order;
    }

    private OrderMain requireOrder(Long id) {
        OrderMain order = getById(id);
        if (order == null) {
            throw new BusinessException("Order not found");
        }
        return order;
    }

    private List<OrderItem> loadItems(Long orderId) {
        return orderItemMapper.selectList(new LambdaQueryWrapper<OrderItem>()
                .eq(OrderItem::getOrderId, orderId));
    }

    private PageResult<OrderResponse> toPageResult(Page<OrderMain> page, boolean includeUser) {
        List<OrderResponse> records = new ArrayList<OrderResponse>();
        for (OrderMain order : page.getRecords()) {
            records.add(toResponse(order, loadItems(order.getId()), includeUser));
        }
        return new PageResult<OrderResponse>(records, page.getTotal(), page.getCurrent(), page.getSize());
    }

    private OrderResponse toResponse(OrderMain order, List<OrderItem> items, boolean includeUser) {
        OrderResponse response = new OrderResponse();
        response.setId(order.getId());
        response.setOrderNo(order.getOrderNo());
        response.setUserId(order.getUserId());
        response.setTotalAmount(order.getTotalAmount());
        response.setStatus(order.getStatus());
        response.setReceiverName(order.getReceiverName());
        response.setReceiverPhone(order.getReceiverPhone());
        response.setReceiverAddress(order.getReceiverAddress());
        response.setCreatedAt(order.getCreatedAt());
        response.setPaidAt(order.getPaidAt());
        if (includeUser) {
            SysUser user = userService.getById(order.getUserId());
            if (user != null) {
                response.setUsername(user.getUsername());
                response.setNickname(user.getNickname());
            }
        }
        List<OrderItemResponse> itemResponses = new ArrayList<OrderItemResponse>();
        for (OrderItem item : items) {
            OrderItemResponse itemResponse = new OrderItemResponse();
            itemResponse.setId(item.getId());
            itemResponse.setProductId(item.getProductId());
            itemResponse.setProductName(item.getProductName());
            itemResponse.setProductImage(item.getProductImage());
            itemResponse.setPrice(item.getPrice());
            itemResponse.setQuantity(item.getQuantity());
            itemResponse.setTotalAmount(item.getTotalAmount());
            itemResponses.add(itemResponse);
        }
        response.setItems(itemResponses);
        return response;
    }

    private void writeInventory(Long productId, Integer changeQuantity, Integer beforeStock, Integer afterStock, String businessType, Long businessId) {
        InventoryRecord record = new InventoryRecord();
        record.setProductId(productId);
        record.setChangeQuantity(changeQuantity);
        record.setBeforeStock(beforeStock);
        record.setAfterStock(afterStock);
        record.setBusinessType(businessType);
        record.setBusinessId(businessId);
        inventoryRecordMapper.insert(record);
    }

    private String generateOrderNo() {
        return "O" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmssSSS"))
                + ThreadLocalRandom.current().nextInt(1000, 10000);
    }
}
