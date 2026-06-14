package com.example.aicommerce.ai.controller;

import com.example.aicommerce.ai.dto.AiMessageRequest;
import com.example.aicommerce.ai.dto.AiResponse;
import com.example.aicommerce.ai.dto.OperationAnalysisRequest;
import com.example.aicommerce.ai.dto.ProductCopywritingRequest;
import com.example.aicommerce.ai.dto.ProductQaRequest;
import com.example.aicommerce.ai.service.AiService;
import com.example.aicommerce.common.ApiResponse;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai")
public class AiController {
    private final AiService aiService;

    public AiController(AiService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/shopping-guide")
    public ApiResponse<AiResponse> shoppingGuide(@Validated @RequestBody AiMessageRequest request) {
        return ApiResponse.ok(aiService.shoppingGuide(request));
    }

    @PostMapping("/product-qa")
    public ApiResponse<AiResponse> productQa(@Validated @RequestBody ProductQaRequest request) {
        return ApiResponse.ok(aiService.productQa(request));
    }

    @PostMapping("/product-copywriting")
    public ApiResponse<AiResponse> productCopywriting(@Validated @RequestBody ProductCopywritingRequest request) {
        return ApiResponse.ok(aiService.productCopywriting(request));
    }

    @PostMapping("/operation-analysis")
    public ApiResponse<AiResponse> operationAnalysis(@RequestBody OperationAnalysisRequest request) {
        return ApiResponse.ok(aiService.operationAnalysis(request));
    }
}
