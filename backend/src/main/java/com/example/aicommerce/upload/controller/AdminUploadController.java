package com.example.aicommerce.upload.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.upload.dto.UploadResponse;
import com.example.aicommerce.upload.service.OssUploadService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/admin/uploads")
public class AdminUploadController {
    private final OssUploadService uploadService;

    public AdminUploadController(OssUploadService uploadService) {
        this.uploadService = uploadService;
    }

    @PostMapping("/product-images")
    public ApiResponse<UploadResponse> uploadProductImage(@RequestParam("file") MultipartFile file) {
        return ApiResponse.ok(uploadService.uploadProductImage(file));
    }
}
