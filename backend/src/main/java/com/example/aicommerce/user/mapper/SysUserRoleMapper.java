package com.example.aicommerce.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.aicommerce.user.entity.SysUserRole;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface SysUserRoleMapper extends BaseMapper<SysUserRole> {
    @Select("select r.code from sys_role r inner join sys_user_role ur on ur.role_id = r.id where ur.user_id = #{userId}")
    List<String> selectRoleCodesByUserId(Long userId);

    @Delete("delete from sys_user_role where user_id = #{userId}")
    int deleteByUserId(Long userId);
}

