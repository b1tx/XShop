package com.example.aicommerce.ai.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.aicommerce.ai.dto.AiMessageRequest;
import com.example.aicommerce.ai.dto.AiResponse;
import com.example.aicommerce.ai.dto.OperationAnalysisRequest;
import com.example.aicommerce.ai.dto.ProductCopywritingRequest;
import com.example.aicommerce.ai.dto.ProductQaRequest;
import com.example.aicommerce.ai.entity.AiChatRecord;
import com.example.aicommerce.ai.mapper.AiChatRecordMapper;
import com.example.aicommerce.product.entity.Product;
import com.example.aicommerce.product.service.ProductService;
import com.example.aicommerce.security.CurrentUser;
import com.example.aicommerce.security.CurrentUserHolder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AiServiceImpl implements AiService {
    private final ProductService productService;
    private final AiChatRecordMapper recordMapper;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${ai.openai-compatible.base-url:https://api.openai.com/v1}")
    private String baseUrl;

    @Value("${ai.openai-compatible.api-key:}")
    private String apiKey;

    @Value("${ai.openai-compatible.model:gpt-4o-mini}")
    private String model;

    public AiServiceImpl(ProductService productService, AiChatRecordMapper recordMapper) {
        this.productService = productService;
        this.recordMapper = recordMapper;
    }

    @Override
    public AiResponse shoppingGuide(AiMessageRequest request) {
        List<Product> products = productService.list(new LambdaQueryWrapper<Product>()
                .eq(Product::getStatus, 1)
                .orderByDesc(Product::getCreatedAt)
                .last("LIMIT 6"));
        String prompt = "你是哥特风网上店铺导购。用户需求：" + request.getMessage()
                + "\n可推荐商品：" + productBrief(products)
                + "\n请输出简短购买建议，并给出推荐理由。";
        String fallback = "推荐从黑色斗篷、银色项链和乌木香氛中选择：斗篷适合造型主件，项链提升细节，香氛适合作为低预算礼物。";
        return complete("SHOPPING_GUIDE", prompt, fallback, productIds(products));
    }

    @Override
    public AiResponse productQa(ProductQaRequest request) {
        Product product = productService.getById(request.getProductId());
        String productText = product == null ? "未知商品" : product.getName() + "，" + product.getSubtitle() + "，详情：" + product.getDetail();
        String prompt = "请基于商品信息回答用户问题。\n商品：" + productText + "\n问题：" + request.getQuestion();
        String fallback = product == null
                ? "暂时没有找到该商品信息，请返回商品页重新选择。"
                : "这件商品适合喜欢暗色、复古和低调质感的用户。建议结合库存、价格和页面详情判断是否购买。";
        return complete("PRODUCT_QA", prompt, fallback, request.getProductId() == null ? Collections.<Long>emptyList() : Collections.singletonList(request.getProductId()));
    }

    @Override
    public AiResponse productCopywriting(ProductCopywritingRequest request) {
        String prompt = "为哥特风商品生成电商标题、卖点和详情短文。商品名：" + request.getProductName()
                + "，卖点：" + request.getSellingPoints() + "，目标用户：" + request.getTargetUser();
        String fallback = request.getProductName() + "：以暗色质感和复古轮廓为核心，适合日常搭配与主题造型。卖点包括材质稳定、风格鲜明、易于搭配。";
        return complete("PRODUCT_COPYWRITING", prompt, fallback, Collections.<Long>emptyList());
    }

    @Override
    public AiResponse operationAnalysis(OperationAnalysisRequest request) {
        String prompt = "请为哥特风电商店铺做运营分析。时间范围：" + request.getDateRange()
                + "，关注点：" + request.getFocus() + "。请输出销售观察、库存风险、补货建议和促销建议。";
        String fallback = "运营建议：优先关注高客单价服饰和饰品库存；低库存商品应及时补货；香氛、灯具适合做组合促销；已支付未发货订单需要优先处理。";
        return complete("OPERATION_ANALYSIS", prompt, fallback, Collections.<Long>emptyList());
    }

    @SuppressWarnings("unchecked")
    private AiResponse complete(String scene, String prompt, String fallback, List<Long> productIds) {
        boolean fallbackUsed = true;
        String content = fallback;
        if (StringUtils.hasText(apiKey)) {
            try {
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                headers.setBearerAuth(apiKey);

                Map<String, Object> body = new HashMap<String, Object>();
                body.put("model", model);
                body.put("temperature", 0.7);
                List<Map<String, String>> messages = new ArrayList<Map<String, String>>();
                messages.add(message("system", "你是 B2C 电商系统中的中文 AI 助手，回答要简洁、可执行。"));
                messages.add(message("user", prompt));
                body.put("messages", messages);

                Map<String, Object> result = restTemplate.postForObject(
                        trimSlash(baseUrl) + "/chat/completions",
                        new HttpEntity<Map<String, Object>>(body, headers),
                        Map.class);
                List<Map<String, Object>> choices = result == null ? null : (List<Map<String, Object>>) result.get("choices");
                if (choices != null && !choices.isEmpty()) {
                    Map<String, Object> msg = (Map<String, Object>) choices.get(0).get("message");
                    if (msg != null && StringUtils.hasText((String) msg.get("content"))) {
                        content = (String) msg.get("content");
                        fallbackUsed = false;
                    }
                }
            } catch (Exception ignored) {
                fallbackUsed = true;
                content = fallback;
            }
        }
        saveRecord(scene, prompt, content);
        AiResponse response = new AiResponse();
        response.setScene(scene);
        response.setContent(content);
        response.setModel(model);
        response.setFallback(fallbackUsed);
        response.setRecommendedProductIds(productIds);
        return response;
    }

    private Map<String, String> message(String role, String content) {
        Map<String, String> message = new HashMap<String, String>();
        message.put("role", role);
        message.put("content", content);
        return message;
    }

    private void saveRecord(String scene, String prompt, String response) {
        Long userId = null;
        try {
            CurrentUser user = CurrentUserHolder.getRequiredUser();
            userId = user.getId();
        } catch (RuntimeException ignored) {
            userId = null;
        }
        AiChatRecord record = new AiChatRecord();
        record.setUserId(userId);
        record.setScene(scene);
        record.setPrompt(prompt);
        record.setResponse(response);
        record.setModel(model);
        recordMapper.insert(record);
    }

    private List<Long> productIds(List<Product> products) {
        List<Long> ids = new ArrayList<Long>();
        for (Product product : products) {
            ids.add(product.getId());
        }
        return ids;
    }

    private String productBrief(List<Product> products) {
        StringBuilder builder = new StringBuilder();
        for (Product product : products) {
            builder.append(product.getId()).append("：")
                    .append(product.getName()).append("，")
                    .append(product.getSubtitle()).append("，价格")
                    .append(product.getPrice()).append("；");
        }
        return builder.toString();
    }

    private String trimSlash(String value) {
        if (!StringUtils.hasText(value)) {
            return "https://api.openai.com/v1";
        }
        return value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
    }
}
