<template>
  <main class="admin-shell">
    <aside class="sidebar">
      <h1>AI 电商后台</h1>
      <RouterLink to="/admin">销售看板</RouterLink>
      <RouterLink to="/admin/products">商品管理</RouterLink>
      <RouterLink to="/admin/orders">订单管理</RouterLink>
      <RouterLink to="/admin/promotions">促销管理</RouterLink>
      <RouterLink to="/admin/ai-operation">AI 运营助手</RouterLink>
      <RouterLink class="active" to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/">返回店铺</RouterLink>
    </aside>

    <section class="admin-content">
      <header class="admin-header">
        <div>
          <p class="eyebrow">Users</p>
          <h2>用户管理</h2>
        </div>
      </header>

      <section class="table-panel">
        <div class="admin-filter">
          <el-input v-model="query.keyword" clearable placeholder="搜索用户名或昵称" />
          <el-button type="primary" @click="loadUsers">查询</el-button>
        </div>

        <el-table :data="users" style="width: 100%">
          <el-table-column prop="username" label="用户名" width="140" />
          <el-table-column prop="nickname" label="昵称" width="140" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column label="角色" min-width="220">
            <template #default="{ row }">
              <el-select
                :model-value="row.roles"
                multiple
                collapse-tags
                @change="(roles: string[]) => saveRoles(row.id, roles)"
              >
                <el-option label="普通用户" value="USER" />
                <el-option label="运营管理员" value="OPERATOR" />
                <el-option label="系统管理员" value="ADMIN" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-switch
                :model-value="row.status"
                :active-value="1"
                :inactive-value="0"
                @change="(status: number) => saveStatus(row.id, status)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="190" />
        </el-table>

        <el-pagination
          class="admin-pagination"
          layout="prev, pager, next"
          :current-page="query.page"
          :page-size="query.size"
          :total="total"
          @current-change="handlePageChange"
        />
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminUsers, updateAdminUserRoles, updateAdminUserStatus, type AdminUser } from '../api/admin'
import type { EntityId } from '../types/product'

const users = ref<AdminUser[]>([])
const total = ref(0)
const query = reactive({
  page: 1,
  size: 10,
  keyword: ''
})

async function loadUsers() {
  const page = await getAdminUsers(query)
  users.value = page.records
  total.value = page.total
}

async function saveStatus(id: EntityId, status: number) {
  await updateAdminUserStatus(id, status)
  ElMessage.success('状态已更新')
  await loadUsers()
}

async function saveRoles(id: EntityId, roles: string[]) {
  await updateAdminUserRoles(id, roles)
  ElMessage.success('角色已更新')
  await loadUsers()
}

function handlePageChange(page: number) {
  query.page = page
  loadUsers()
}

onMounted(loadUsers)
</script>
