package com.example.aicommerce.promotion.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.order.dto.OrderResponse;
import com.example.aicommerce.order.service.OrderService;
import com.example.aicommerce.product.entity.Product;
import com.example.aicommerce.product.service.ProductService;
import com.example.aicommerce.promotion.dto.PromotionOrderRequest;
import com.example.aicommerce.promotion.dto.PromotionProductRequest;
import com.example.aicommerce.promotion.dto.PromotionProductResponse;
import com.example.aicommerce.promotion.dto.PromotionRequest;
import com.example.aicommerce.promotion.dto.PromotionResponse;
import com.example.aicommerce.promotion.entity.PromotionActivity;
import com.example.aicommerce.promotion.entity.PromotionProduct;
import com.example.aicommerce.promotion.mapper.PromotionActivityMapper;
import com.example.aicommerce.promotion.mapper.PromotionProductMapper;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Service
public class PromotionServiceImpl implements PromotionService {
    private static final String STOCK_KEY_PREFIX = "promotion:stock:";

    private final PromotionActivityMapper activityMapper;
    private final PromotionProductMapper promotionProductMapper;
    private final ProductService productService;
    private final OrderService orderService;
    private final StringRedisTemplate redisTemplate;

    public PromotionServiceImpl(PromotionActivityMapper activityMapper,
                                PromotionProductMapper promotionProductMapper,
                                ProductService productService,
                                OrderService orderService,
                                StringRedisTemplate redisTemplate) {
        this.activityMapper = activityMapper;
        this.promotionProductMapper = promotionProductMapper;
        this.productService = productService;
        this.orderService = orderService;
        this.redisTemplate = redisTemplate;
    }

    @Override
    public List<PromotionResponse> listActivePromotions() {
        LocalDateTime now = LocalDateTime.now();
        List<PromotionActivity> activities = activityMapper.selectList(new LambdaQueryWrapper<PromotionActivity>()
                .eq(PromotionActivity::getStatus, 1)
                .le(PromotionActivity::getStartTime, now)
                .ge(PromotionActivity::getEndTime, now)
                .orderByAsc(PromotionActivity::getEndTime));
        List<PromotionResponse> responses = new ArrayList<PromotionResponse>();
        for (PromotionActivity activity : activities) {
            responses.add(toResponse(activity, true));
        }
        return responses;
    }

    @Override
    public PromotionResponse getPromotion(Long id, boolean admin) {
        PromotionActivity activity = requireActivity(id);
        if (!admin && (activity.getStatus() == null || activity.getStatus() != 1)) {
            throw new BusinessException("活动不可用");
        }
        return toResponse(activity, true);
    }

    @Override
    public PageResult<PromotionResponse> pageAdminPromotions(long page, long size, String keyword, Integer status) {
        LambdaQueryWrapper<PromotionActivity> wrapper = new LambdaQueryWrapper<PromotionActivity>()
                .orderByDesc(PromotionActivity::getCreatedAt);
        if (StringUtils.hasText(keyword)) {
            wrapper.like(PromotionActivity::getName, keyword);
        }
        if (status != null) {
            wrapper.eq(PromotionActivity::getStatus, status);
        }
        Page<PromotionActivity> activityPage = activityMapper.selectPage(new Page<PromotionActivity>(page, size), wrapper);
        List<PromotionResponse> records = new ArrayList<PromotionResponse>();
        for (PromotionActivity activity : activityPage.getRecords()) {
            records.add(toResponse(activity, true));
        }
        return new PageResult<PromotionResponse>(records, activityPage.getTotal(), activityPage.getCurrent(), activityPage.getSize());
    }

    @Override
    @Transactional
    public PromotionResponse create(PromotionRequest request) {
        validateTime(request);
        PromotionActivity activity = new PromotionActivity();
        applyActivity(activity, request);
        activityMapper.insert(activity);
        saveProducts(activity.getId(), request.getProducts());
        return toResponse(activity, true);
    }

    @Override
    @Transactional
    public PromotionResponse update(Long id, PromotionRequest request) {
        PromotionActivity activity = requireActivity(id);
        validateTime(request);
        applyActivity(activity, request);
        activityMapper.updateById(activity);
        if (request.getProducts() != null) {
            promotionProductMapper.delete(new LambdaQueryWrapper<PromotionProduct>()
                    .eq(PromotionProduct::getActivityId, id));
            saveProducts(id, request.getProducts());
        }
        return toResponse(activity, true);
    }

    @Override
    public void updateStatus(Long id, Integer status) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BusinessException("活动状态不正确");
        }
        PromotionActivity activity = requireActivity(id);
        activity.setStatus(status);
        activityMapper.updateById(activity);
        if (status == 1) {
            for (PromotionProduct product : listProducts(activity.getId())) {
                ensureRedisStock(product);
            }
        }
    }

    @Override
    public OrderResponse createPromotionOrder(Long activityId, PromotionOrderRequest request) {
        PromotionActivity activity = requireActivity(activityId);
        validateActive(activity);
        PromotionProduct promotionProduct = promotionProductMapper.selectById(request.getPromotionProductId());
        if (promotionProduct == null || !activityId.equals(promotionProduct.getActivityId())) {
            throw new BusinessException("活动商品不存在");
        }
        int quantity = request.getQuantity() == null ? 1 : request.getQuantity();
        if (quantity < 1) {
            throw new BusinessException("购买数量必须大于 0");
        }
        if (promotionProduct.getLimitPerUser() != null && quantity > promotionProduct.getLimitPerUser()) {
            throw new BusinessException("超过单次限购数量");
        }
        ensureRedisStock(promotionProduct);
        Long remaining = redisTemplate.opsForValue().decrement(stockKey(promotionProduct.getId()), quantity);
        if (remaining == null || remaining < 0) {
            redisTemplate.opsForValue().increment(stockKey(promotionProduct.getId()), quantity);
            throw new BusinessException("活动库存不足");
        }
        try {
            return orderService.createDirectOrder(
                    promotionProduct.getProductId(),
                    quantity,
                    promotionProduct.getPromotionPrice(),
                    promotionProduct.getId(),
                    request.getReceiverName(),
                    request.getReceiverPhone(),
                    request.getReceiverAddress(),
                    "PROMOTION_ORDER");
        } catch (RuntimeException ex) {
            redisTemplate.opsForValue().increment(stockKey(promotionProduct.getId()), quantity);
            throw ex;
        }
    }

    private void applyActivity(PromotionActivity activity, PromotionRequest request) {
        activity.setName(request.getName());
        activity.setStartTime(request.getStartTime());
        activity.setEndTime(request.getEndTime());
        activity.setStatus(request.getStatus() == null ? 0 : request.getStatus());
    }

    private void validateTime(PromotionRequest request) {
        if (request.getStartTime() != null && request.getEndTime() != null
                && !request.getEndTime().isAfter(request.getStartTime())) {
            throw new BusinessException("结束时间必须晚于开始时间");
        }
    }

    private void validateActive(PromotionActivity activity) {
        if (activity.getStatus() == null || activity.getStatus() != 1) {
            throw new BusinessException("活动未启用");
        }
        LocalDateTime now = LocalDateTime.now();
        if (now.isBefore(activity.getStartTime())) {
            throw new BusinessException("活动尚未开始");
        }
        if (now.isAfter(activity.getEndTime())) {
            throw new BusinessException("活动已结束");
        }
    }

    private void saveProducts(Long activityId, List<PromotionProductRequest> requests) {
        if (requests == null) {
            return;
        }
        for (PromotionProductRequest request : requests) {
            Product product = productService.getById(request.getProductId());
            if (product == null) {
                throw new BusinessException("活动商品不存在");
            }
            PromotionProduct promotionProduct = new PromotionProduct();
            promotionProduct.setActivityId(activityId);
            promotionProduct.setProductId(request.getProductId());
            promotionProduct.setPromotionPrice(request.getPromotionPrice());
            promotionProduct.setPromotionStock(request.getPromotionStock());
            promotionProduct.setLimitPerUser(request.getLimitPerUser() == null ? 1 : request.getLimitPerUser());
            promotionProductMapper.insert(promotionProduct);
            redisTemplate.opsForValue().set(stockKey(promotionProduct.getId()), String.valueOf(promotionProduct.getPromotionStock()));
        }
    }

    private PromotionActivity requireActivity(Long id) {
        PromotionActivity activity = activityMapper.selectById(id);
        if (activity == null) {
            throw new BusinessException("活动不存在");
        }
        return activity;
    }

    private List<PromotionProduct> listProducts(Long activityId) {
        return promotionProductMapper.selectList(new LambdaQueryWrapper<PromotionProduct>()
                .eq(PromotionProduct::getActivityId, activityId));
    }

    private PromotionResponse toResponse(PromotionActivity activity, boolean includeProducts) {
        PromotionResponse response = new PromotionResponse();
        response.setId(activity.getId());
        response.setName(activity.getName());
        response.setStartTime(activity.getStartTime());
        response.setEndTime(activity.getEndTime());
        response.setStatus(activity.getStatus());
        response.setCreatedAt(activity.getCreatedAt());
        response.setTimeStatus(timeStatus(activity));
        if (includeProducts) {
            List<PromotionProductResponse> products = new ArrayList<PromotionProductResponse>();
            for (PromotionProduct promotionProduct : listProducts(activity.getId())) {
                products.add(toProductResponse(promotionProduct));
            }
            response.setProducts(products);
        } else {
            response.setProducts(Collections.<PromotionProductResponse>emptyList());
        }
        return response;
    }

    private PromotionProductResponse toProductResponse(PromotionProduct promotionProduct) {
        Product product = productService.getById(promotionProduct.getProductId());
        PromotionProductResponse response = new PromotionProductResponse();
        response.setId(promotionProduct.getId());
        response.setActivityId(promotionProduct.getActivityId());
        response.setProductId(promotionProduct.getProductId());
        if (product != null) {
            response.setProductName(product.getName());
            response.setSubtitle(product.getSubtitle());
            response.setMainImage(product.getMainImage());
            response.setOriginalPrice(product.getPrice());
        }
        response.setPromotionPrice(promotionProduct.getPromotionPrice());
        response.setPromotionStock(promotionProduct.getPromotionStock());
        response.setRemainingStock(readRedisStock(promotionProduct));
        response.setLimitPerUser(promotionProduct.getLimitPerUser());
        return response;
    }

    private Integer readRedisStock(PromotionProduct promotionProduct) {
        ensureRedisStock(promotionProduct);
        String value = redisTemplate.opsForValue().get(stockKey(promotionProduct.getId()));
        return value == null ? promotionProduct.getPromotionStock() : Integer.valueOf(value);
    }

    private void ensureRedisStock(PromotionProduct promotionProduct) {
        String key = stockKey(promotionProduct.getId());
        Boolean exists = redisTemplate.hasKey(key);
        if (exists == null || !exists) {
            redisTemplate.opsForValue().set(key, String.valueOf(promotionProduct.getPromotionStock()));
        }
    }

    private String stockKey(Long promotionProductId) {
        return STOCK_KEY_PREFIX + promotionProductId;
    }

    private String timeStatus(PromotionActivity activity) {
        LocalDateTime now = LocalDateTime.now();
        if (now.isBefore(activity.getStartTime())) {
            return "NOT_STARTED";
        }
        if (now.isAfter(activity.getEndTime())) {
            return "ENDED";
        }
        return activity.getStatus() != null && activity.getStatus() == 1 ? "ACTIVE" : "DISABLED";
    }
}
