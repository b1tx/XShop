package com.example.aicommerce.user.dto;

import lombok.Data;

import javax.validation.constraints.NotEmpty;
import java.util.List;

@Data
public class UpdateUserRolesRequest {
    @NotEmpty
    private List<String> roles;
}

