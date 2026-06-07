package com.example.aicommerce.auth.service;

import com.example.aicommerce.auth.dto.LoginRequest;
import com.example.aicommerce.auth.dto.LoginResponse;
import com.example.aicommerce.auth.dto.RegisterRequest;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.security.CurrentUserHolder;
import com.example.aicommerce.security.JwtTokenProvider;
import com.example.aicommerce.user.dto.UserProfileResponse;
import com.example.aicommerce.user.entity.SysRole;
import com.example.aicommerce.user.entity.SysUser;
import com.example.aicommerce.user.mapper.SysRoleMapper;
import com.example.aicommerce.user.service.UserService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;

@Service
public class AuthService {
    private final UserService userService;
    private final SysRoleMapper roleMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public AuthService(UserService userService, SysRoleMapper roleMapper, PasswordEncoder passwordEncoder, JwtTokenProvider jwtTokenProvider) {
        this.userService = userService;
        this.roleMapper = roleMapper;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Transactional
    public LoginResponse register(RegisterRequest request) {
        if (userService.findByUsername(request.getUsername()) != null) {
            throw new BusinessException("用户名已存在");
        }
        SysRole userRole = roleMapper.selectOne(new LambdaQueryWrapper<SysRole>().eq(SysRole::getCode, "USER"));
        if (userRole == null) {
            throw new BusinessException("USER 角色未初始化");
        }
        SysUser user = new SysUser();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setNickname(request.getNickname());
        user.setPhone(request.getPhone());
        user.setStatus(1);
        userService.save(user);
        userService.assignRoles(user.getId(), Collections.singletonList("USER"));
        return createLoginResponse(user);
    }

    public LoginResponse login(LoginRequest request) {
        SysUser user = userService.findByUsername(request.getUsername());
        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(401, "用户名或密码错误");
        }
        if (user.getStatus() == null || user.getStatus() != 1) {
            throw new BusinessException(403, "用户已禁用");
        }
        return createLoginResponse(user);
    }

    public UserProfileResponse profile() {
        return userService.toProfile(userService.getById(CurrentUserHolder.getRequiredUser().getId()));
    }

    private LoginResponse createLoginResponse(SysUser user) {
        return new LoginResponse(jwtTokenProvider.createToken(user.getUsername()), userService.toProfile(user));
    }
}

