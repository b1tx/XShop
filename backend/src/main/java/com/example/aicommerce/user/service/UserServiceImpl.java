package com.example.aicommerce.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.common.PageResult;
import com.example.aicommerce.security.CurrentUser;
import com.example.aicommerce.user.dto.UserListItem;
import com.example.aicommerce.user.dto.UserProfileResponse;
import com.example.aicommerce.user.entity.SysRole;
import com.example.aicommerce.user.entity.SysUser;
import com.example.aicommerce.user.entity.SysUserRole;
import com.example.aicommerce.user.mapper.SysRoleMapper;
import com.example.aicommerce.user.mapper.SysUserMapper;
import com.example.aicommerce.user.mapper.SysUserRoleMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class UserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements UserService {
    private final SysUserRoleMapper userRoleMapper;
    private final SysRoleMapper roleMapper;

    public UserServiceImpl(SysUserRoleMapper userRoleMapper, SysRoleMapper roleMapper) {
        this.userRoleMapper = userRoleMapper;
        this.roleMapper = roleMapper;
    }

    @Override
    public SysUser findByUsername(String username) {
        return getOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username), false);
    }

    @Override
    public CurrentUser loadCurrentUser(String username) {
        SysUser user = findByUsername(username);
        if (user == null || user.getStatus() == null || user.getStatus() != 1) {
            throw new BusinessException(401, "用户不存在或已禁用");
        }
        return new CurrentUser(user.getId(), user.getUsername(), user.getNickname(), getRoleCodes(user.getId()));
    }

    @Override
    public List<String> getRoleCodes(Long userId) {
        return userRoleMapper.selectRoleCodesByUserId(userId);
    }

    @Override
    @Transactional
    public void assignRoles(Long userId, List<String> roleCodes) {
        SysUser user = getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        List<SysRole> roles = roleMapper.selectList(new LambdaQueryWrapper<SysRole>().in(SysRole::getCode, roleCodes));
        if (roles.size() != roleCodes.size()) {
            throw new BusinessException("角色不存在");
        }
        userRoleMapper.deleteByUserId(userId);
        for (SysRole role : roles) {
            SysUserRole userRole = new SysUserRole();
            userRole.setUserId(userId);
            userRole.setRoleId(role.getId());
            userRoleMapper.insert(userRole);
        }
    }

    @Override
    public UserProfileResponse toProfile(SysUser user) {
        return new UserProfileResponse(
                user.getId(),
                user.getUsername(),
                user.getNickname(),
                user.getPhone(),
                user.getStatus(),
                getRoleCodes(user.getId())
        );
    }

    @Override
    public PageResult<UserListItem> pageUsers(long page, long size, String keyword) {
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<SysUser>()
                .orderByDesc(SysUser::getCreatedAt);
        if (StringUtils.hasText(keyword)) {
            wrapper.and(query -> query.like(SysUser::getUsername, keyword).or().like(SysUser::getNickname, keyword));
        }
        Page<SysUser> userPage = page(new Page<SysUser>(page, size), wrapper);
        List<UserListItem> records = new ArrayList<UserListItem>();
        for (SysUser user : userPage.getRecords()) {
            UserListItem item = new UserListItem();
            item.setId(user.getId());
            item.setUsername(user.getUsername());
            item.setNickname(user.getNickname());
            item.setPhone(user.getPhone());
            item.setStatus(user.getStatus());
            item.setCreatedAt(user.getCreatedAt());
            item.setRoles(getRoleCodes(user.getId()));
            records.add(item);
        }
        return new PageResult<UserListItem>(records, userPage.getTotal(), userPage.getCurrent(), userPage.getSize());
    }

    @Override
    public void updateStatus(Long id, Integer status) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BusinessException("状态值不正确");
        }
        SysUser user = getById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        user.setStatus(status);
        updateById(user);
    }
}

