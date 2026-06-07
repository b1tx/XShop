package com.example.aicommerce.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

public final class CurrentUserHolder {
    private CurrentUserHolder() {
    }

    public static CurrentUser getRequiredUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !(authentication.getPrincipal() instanceof CurrentUser)) {
            throw new IllegalStateException("用户未登录");
        }
        return (CurrentUser) authentication.getPrincipal();
    }
}

