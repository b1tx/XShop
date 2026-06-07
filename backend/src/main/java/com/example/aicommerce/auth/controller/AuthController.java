package com.example.aicommerce.auth.controller;

import com.example.aicommerce.auth.dto.LoginRequest;
import com.example.aicommerce.auth.dto.LoginResponse;
import com.example.aicommerce.auth.dto.RegisterRequest;
import com.example.aicommerce.auth.service.AuthService;
import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.user.dto.UserProfileResponse;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/register")
    public ApiResponse<LoginResponse> register(@Validated @RequestBody RegisterRequest request) {
        return ApiResponse.ok(authService.register(request));
    }

    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Validated @RequestBody LoginRequest request) {
        return ApiResponse.ok(authService.login(request));
    }

    @GetMapping("/profile")
    public ApiResponse<UserProfileResponse> profile() {
        return ApiResponse.ok(authService.profile());
    }
}

