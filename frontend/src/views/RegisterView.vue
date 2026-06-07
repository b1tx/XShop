<template>
  <main class="auth-shell">
    <section class="auth-panel">
      <p class="eyebrow">Create Account</p>
      <h1>注册普通用户</h1>
      <el-form :model="form" label-position="top" @submit.prevent="handleRegister">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-button type="primary" :loading="loading" @click="handleRegister">注册并登录</el-button>
      </el-form>
      <p class="auth-link">已有账号？<RouterLink to="/login">返回登录</RouterLink></p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '../api/auth'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const form = reactive({
  username: '',
  nickname: '',
  phone: '',
  password: ''
})

async function handleRegister() {
  loading.value = true
  try {
    const response = await register(form)
    authStore.setSession(response.token, response.user)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

