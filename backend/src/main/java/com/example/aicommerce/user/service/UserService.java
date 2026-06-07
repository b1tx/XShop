package com.example.aicommerce.user.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.security.CurrentUser;
import com.example.aicommerce.user.dto.UserListItem;
import com.example.aicommerce.user.dto.UserProfileResponse;
import com.example.aicommerce.user.entity.SysUser;

import java.util.List;

public interface UserService extends IService<SysUser> {
    SysUser findByUsername(String username);
    CurrentUser loadCurrentUser(String username);
    List<String> getRoleCodes(Long userId);
    void assignRoles(Long userId, List<String> roleCodes);
    UserProfileResponse toProfile(SysUser user);
    PageResult<UserListItem> pageUsers(long page, long size, String keyword);
    void updateStatus(Long id, Integer status);
}

