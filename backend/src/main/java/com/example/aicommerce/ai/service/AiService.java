package com.example.aicommerce.ai.service;

import com.example.aicommerce.ai.dto.AiMessageRequest;
import com.example.aicommerce.ai.dto.AiResponse;
import com.example.aicommerce.ai.dto.OperationAnalysisRequest;
import com.example.aicommerce.ai.dto.ProductCopywritingRequest;
import com.example.aicommerce.ai.dto.ProductQaRequest;

public interface AiService {
    AiResponse shoppingGuide(AiMessageRequest request);

    AiResponse productQa(ProductQaRequest request);

    AiResponse productCopywriting(ProductCopywritingRequest request);

    AiResponse operationAnalysis(OperationAnalysisRequest request);
}
