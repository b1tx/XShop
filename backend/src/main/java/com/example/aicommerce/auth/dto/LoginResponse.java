package com.example.aicommerce.auth.dto;

import com.example.aicommerce.user.dto.UserProfileResponse;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {
    private String token;
    private UserProfileResponse user;
}

