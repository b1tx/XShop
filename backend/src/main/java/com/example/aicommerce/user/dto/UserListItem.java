package com.example.aicommerce.user.dto;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class UserListItem {
    private Long id;
    private String username;
    private String nickname;
    private String phone;
    private Integer status;
    private List<String> roles;
    private LocalDateTime createdAt;
}

