<template>
  <main class="admin-shell">
    <aside class="sidebar">
      <h1>AI 电商后台</h1>
      <RouterLink to="/admin">销售看板</RouterLink>
      <RouterLink to="/admin/products">商品管理</RouterLink>
      <RouterLink to="/admin/orders">订单管理</RouterLink>
      <RouterLink class="active" to="/admin/promotions">促销管理</RouterLink>
      <RouterLink to="/admin/ai-operation">AI 运营助手</RouterLink>
      <RouterLink to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/">返回店铺</RouterLink>
    </aside>

    <section class="admin-content">
      <header class="admin-header">
        <div>
          <p class="eyebrow">Promotions</p>
          <h2>促销管理</h2>
        </div>
        <el-button type="primary" @click="openCreate">新增活动</el-button>
      </header>

      <section class="table-panel">
        <div class="admin-filters">
          <el-input v-model="query.keyword" placeholder="搜索活动" clearable />
          <el-select v-model="query.status" clearable placeholder="状态">
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
        </div>

        <el-table :data="promotions" style="width: 100%">
          <el-table-column prop="name" label="活动" min-width="160" />
          <el-table-column label="时间" min-width="280">
            <template #default="{ row }">
              {{ formatDateTime(row.startTime) }} 至 {{ formatDateTime(row.endTime) }}
            </template>
          </el-table-column>
          <el-table-column label="活动商品" width="100">
            <template #default="{ row }">{{ row.products?.length || 0 }}</template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="230" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" @click="toggleStatus(row)">{{ row.status === 1 ? '停用' : '启用' }}</el-button>
            </template>
          </el-table-column>
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

    <el-dialog
      v-model="dialogVisible"
      class="admin-editor-dialog"
      :title="editingId ? '编辑活动' : '新增活动'"
      width="min(920px, calc(100vw - 32px))"
    >
      <el-form :model="form" label-position="top">
        <section class="admin-editor-section">
          <div>
            <h3>基础信息</h3>
            <p>设置活动名称、时间和上下线状态。</p>
          </div>
          <div class="admin-editor-grid">
            <el-form-item label="活动名称">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="活动状态">
              <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
            </el-form-item>
            <el-form-item class="admin-editor-grid__wide" label="活动时间">
              <el-date-picker
                v-model="timeRange"
                type="datetimerange"
                start-placeholder="开始"
                end-placeholder="结束"
                value-format="YYYY-MM-DDTHH:mm:ss"
              />
            </el-form-item>
          </div>
        </section>

        <section class="admin-editor-section">
          <div>
            <h3>活动商品</h3>
            <p>配置活动商品、活动价、库存和单人限购数量。</p>
          </div>
          <div class="promotion-editor-products">
            <article v-for="(item, index) in form.products" :key="index">
              <el-select v-model="item.productId" filterable placeholder="选择商品">
                <el-option v-for="product in productOptions" :key="product.id" :label="product.name" :value="product.id" />
              </el-select>
              <el-input-number v-model="item.promotionPrice" :min="0.01" :precision="2" placeholder="活动价" />
              <el-input-number v-model="item.promotionStock" :min="0" placeholder="活动库存" />
              <el-input-number v-model="item.limitPerUser" :min="1" placeholder="限购" />
              <el-button type="danger" text @click="removeProduct(index)">删除</el-button>
            </article>
            <el-button @click="addProduct">添加商品</el-button>
          </div>
        </section>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminProducts } from '../api/admin'
import {
  createAdminPromotion,
  getAdminPromotions,
  updateAdminPromotion,
  updateAdminPromotionStatus
} from '../api/promotions'
import type { EntityId, Product } from '../types/product'
import type { Promotion, PromotionPayload } from '../types/promotion'

const promotions = ref<Promotion[]>([])
const productOptions = ref<Product[]>([])
const total = ref(0)
const dialogVisible = ref(false)
const saving = ref(false)
const editingId = ref<EntityId | null>(null)
const query = reactive({
  page: 1,
  size: 10,
  keyword: '',
  status: null as number | null
})

const form = reactive<PromotionPayload>({
  name: '',
  startTime: '',
  endTime: '',
  status: 1,
  products: []
})

const timeRange = computed({
  get: () => (form.startTime && form.endTime ? [form.startTime, form.endTime] : []),
  set: (value: string[]) => {
    form.startTime = value?.[0] || ''
    form.endTime = value?.[1] || ''
  }
})

function formatDateTime(value: string) {
  return value ? value.replace('T', ' ').slice(0, 16) : ''
}

async function loadPromotions() {
  const page = await getAdminPromotions(query)
  promotions.value = page.records
  total.value = page.total
}

async function loadProducts() {
  const page = await getAdminProducts({ page: 1, size: 100, status: 1 })
  productOptions.value = page.records
}

function reload() {
  query.page = 1
  loadPromotions()
}

function resetForm() {
  editingId.value = null
  form.name = ''
  form.startTime = ''
  form.endTime = ''
  form.status = 1
  form.products = []
}

function openCreate() {
  resetForm()
  addProduct()
  dialogVisible.value = true
}

function openEdit(row: Promotion) {
  editingId.value = row.id
  form.name = row.name
  form.startTime = row.startTime
  form.endTime = row.endTime
  form.status = row.status
  form.products = row.products.map((item) => ({
    productId: item.productId,
    promotionPrice: item.promotionPrice,
    promotionStock: item.promotionStock,
    limitPerUser: item.limitPerUser
  }))
  dialogVisible.value = true
}

function addProduct() {
  form.products.push({ productId: '', promotionPrice: 1, promotionStock: 1, limitPerUser: 1 })
}

function removeProduct(index: number) {
  form.products.splice(index, 1)
}

async function save() {
  if (!form.name || !form.startTime || !form.endTime || !form.products.length) {
    ElMessage.warning('请完整填写活动信息')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateAdminPromotion(editingId.value, form)
    } else {
      await createAdminPromotion(form)
    }
    ElMessage.success('活动已保存')
    dialogVisible.value = false
    await loadPromotions()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleStatus(row: Promotion) {
  await updateAdminPromotionStatus(row.id, row.status === 1 ? 0 : 1)
  ElMessage.success('状态已更新')
  await loadPromotions()
}

function handlePageChange(page: number) {
  query.page = page
  loadPromotions()
}

onMounted(() => {
  loadPromotions()
  loadProducts()
})
</script>
