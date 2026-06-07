package com.example.aicommerce.user.controller;

import com.example.aicommerce.common.ApiResponse;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.user.dto.UpdateUserRolesRequest;
import com.example.aicommerce.user.dto.UserListItem;
import com.example.aicommerce.user.service.UserService;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/users")
public class AdminUserController {
    private final UserService userService;

    public AdminUserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public ApiResponse<PageResult<UserListItem>> pageUsers(
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "10") long size,
            @RequestParam(required = false) String keyword) {
        return ApiResponse.ok(userService.pageUsers(page, size, keyword));
    }

    @PutMapping("/{id}/status")
    public ApiResponse<Void> updateStatus(@PathVariable Long id, @RequestBody Map<String, Integer> body) {
        userService.updateStatus(id, body.get("status"));
        return ApiResponse.ok();
    }

    @PutMapping("/{id}/roles")
    public ApiResponse<Void> updateRoles(@PathVariable Long id, @Validated @RequestBody UpdateUserRolesRequest request) {
        userService.assignRoles(id, request.getRoles());
        return ApiResponse.ok();
    }
}

