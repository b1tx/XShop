package com.example.aicommerce.security;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;

@Data
@AllArgsConstructor
public class CurrentUser {
    private Long id;
    private String username;
    private String nickname;
    private List<String> roles;
}

