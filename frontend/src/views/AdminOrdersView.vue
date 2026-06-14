<template>
  <main class="admin-shell">
    <aside class="sidebar">
      <h1>AI 电商后台</h1>
      <RouterLink to="/admin">销售看板</RouterLink>
      <RouterLink to="/admin/products">商品管理</RouterLink>
      <RouterLink class="active" to="/admin/orders">订单管理</RouterLink>
      <RouterLink to="/admin/promotions">促销管理</RouterLink>
      <RouterLink to="/admin/ai-operation">AI 运营助手</RouterLink>
      <RouterLink to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/">返回店铺</RouterLink>
    </aside>

    <section class="admin-content">
      <header class="admin-header">
        <div>
          <p class="eyebrow">Orders</p>
          <h2>订单管理</h2>
        </div>
      </header>

      <section class="table-panel">
        <div class="admin-filter">
          <el-input v-model="query.keyword" clearable placeholder="订单号 / 收货人 / 电话" />
          <el-select v-model="query.status" clearable placeholder="订单状态">
            <el-option v-for="status in statusOptions" :key="status.value" :label="status.label" :value="status.value" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
        </div>

        <el-table :data="orders" style="width: 100%">
          <el-table-column label="订单" min-width="240">
            <template #default="{ row }">
              <div class="admin-order-cell">
                <strong>{{ row.orderNo }}</strong>
                <span>{{ row.nickname || row.username || `用户 ${row.userId}` }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="收货信息" min-width="240">
            <template #default="{ row }">
              <div class="admin-order-cell">
                <strong>{{ row.receiverName }} · {{ row.receiverPhone }}</strong>
                <span>{{ row.receiverAddress }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="totalAmount" label="金额" width="120">
            <template #default="{ row }">¥{{ formatMoney(row.totalAmount) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusTag(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180" />
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button size="small" :loading="isBusy(row.id, 'detail')" :disabled="isAnyBusy(row.id)" @click="openDetail(row.id)">详情</el-button>
              <el-button
                v-if="row.status === 'PAID'"
                size="small"
                type="primary"
                :loading="isBusy(row.id, 'ship')"
                :disabled="isAnyBusy(row.id)"
                @click="ship(row.id)"
              >
                发货
              </el-button>
              <el-button
                v-if="canCancel(row.status)"
                size="small"
                type="danger"
                :loading="isBusy(row.id, 'cancel')"
                :disabled="isAnyBusy(row.id)"
                @click="cancel(row.id)"
              >
                取消
              </el-button>
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

    <el-drawer v-model="drawerVisible" title="订单详情" size="520px">
      <template v-if="currentOrder">
        <section class="admin-order-detail">
          <div>
            <span>订单号</span>
            <strong>{{ currentOrder.orderNo }}</strong>
          </div>
          <div>
            <span>状态</span>
            <el-tag :type="statusTag(currentOrder.status)">{{ statusLabel(currentOrder.status) }}</el-tag>
          </div>
          <div>
            <span>收货信息</span>
            <strong>{{ currentOrder.receiverName }} · {{ currentOrder.receiverPhone }}</strong>
            <p>{{ currentOrder.receiverAddress }}</p>
          </div>
          <div>
            <span>商品明细</span>
            <article v-for="item in currentOrder.items" :key="item.id" class="admin-order-item">
              <img :src="item.productImage" :alt="item.productName" />
              <div>
                <strong>{{ item.productName }}</strong>
                <span>¥{{ formatMoney(item.price) }} × {{ item.quantity }}</span>
              </div>
              <b>¥{{ formatMoney(item.totalAmount) }}</b>
            </article>
          </div>
          <footer>
            <span>订单金额</span>
            <strong>¥{{ formatMoney(currentOrder.totalAmount) }}</strong>
          </footer>
        </section>
      </template>
    </el-drawer>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cancelAdminOrder, getAdminOrderDetail, getAdminOrders, shipAdminOrder } from '../api/admin'
import type { Order, OrderStatus } from '../types/order'
import type { EntityId } from '../types/product'

const orders = ref<Order[]>([])
const total = ref(0)
const drawerVisible = ref(false)
const currentOrder = ref<Order | null>(null)
const busyActions = ref(new Set<string>())
const query = reactive({
  page: 1,
  size: 10,
  keyword: '',
  status: null as string | null
})

const statusOptions = [
  { label: '待支付', value: 'CREATED' },
  { label: '已支付', value: 'PAID' },
  { label: '已发货', value: 'SHIPPED' },
  { label: '已收货', value: 'RECEIVED' },
  { label: '已取消', value: 'CANCELLED' }
]

function statusLabel(status: OrderStatus) {
  return statusOptions.find((item) => item.value === status)?.label || status
}

function statusTag(status: OrderStatus) {
  if (status === 'PAID') return 'warning'
  if (status === 'SHIPPED') return 'primary'
  if (status === 'RECEIVED') return 'success'
  if (status === 'CANCELLED') return 'info'
  return 'danger'
}

function canCancel(status: OrderStatus) {
  return status === 'CREATED' || status === 'PAID'
}

function formatMoney(value: number) {
  return Number(value || 0).toFixed(2)
}

function actionKey(id: EntityId, action: string) {
  return `${action}:${id}`
}

function setBusy(id: EntityId, action: string, busy: boolean) {
  const next = new Set(busyActions.value)
  const key = actionKey(id, action)
  if (busy) {
    next.add(key)
  } else {
    next.delete(key)
  }
  busyActions.value = next
}

function isBusy(id: EntityId, action: string) {
  return busyActions.value.has(actionKey(id, action))
}

function isAnyBusy(id: EntityId) {
  return ['detail', 'ship', 'cancel'].some((action) => isBusy(id, action))
}

async function loadOrders() {
  try {
    const page = await getAdminOrders(query)
    orders.value = page.records
    total.value = page.total
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '订单加载失败')
  }
}

function reload() {
  query.page = 1
  loadOrders()
}

async function openDetail(id: EntityId) {
  setBusy(id, 'detail', true)
  try {
    currentOrder.value = await getAdminOrderDetail(id)
    drawerVisible.value = true
  } catch (error) {
    currentOrder.value = null
    drawerVisible.value = false
    ElMessage.error(error instanceof Error ? error.message : '订单详情加载失败')
  } finally {
    setBusy(id, 'detail', false)
  }
}

async function ship(id: EntityId) {
  setBusy(id, 'ship', true)
  try {
    await shipAdminOrder(id)
    ElMessage.success('订单已发货')
    await loadOrders()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '发货失败')
  } finally {
    setBusy(id, 'ship', false)
  }
}

async function cancel(id: EntityId) {
  try {
    await ElMessageBox.confirm('确认取消该订单？库存会自动回滚。', '取消订单')
  } catch {
    return
  }
  setBusy(id, 'cancel', true)
  try {
    await cancelAdminOrder(id)
    ElMessage.success('订单已取消')
    await loadOrders()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '取消订单失败')
  } finally {
    setBusy(id, 'cancel', false)
  }
}

function handlePageChange(page: number) {
  query.page = page
  loadOrders()
}

onMounted(loadOrders)
</script>
