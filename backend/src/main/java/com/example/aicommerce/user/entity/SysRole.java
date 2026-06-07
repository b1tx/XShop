package com.example.aicommerce.user.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sys_role")
public class SysRole {
    @TableId
    private Long id;
    private String code;
    private String name;
    private LocalDateTime createdAt;
}

