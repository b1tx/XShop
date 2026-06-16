<template>
  <main class="store-shell gothic-store">
    <header class="gothic-header">
      <div class="store-container gothic-header__inner detail-header">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>XSHOP</strong>
            <small>Orders</small>
          </span>
        </RouterLink>
        <div class="gothic-actions">
          <RouterLink to="/">返回店铺</RouterLink>
          <RouterLink to="/cart">购物车</RouterLink>
        </div>
      </div>
    </header>

    <section class="store-container order-layout">
      <div class="cart-heading">
        <div>
          <p class="eyebrow">Order Center</p>
          <h1>我的订单</h1>
        </div>
        <div class="order-statusbar" aria-label="订单状态筛选">
          <button
            v-for="status in statusFilters"
            :key="status.value || 'ALL'"
            class="order-status-filter"
            :class="{ 'is-active': query.status === status.value }"
            type="button"
            @click="setStatus(status.value)"
          >
            {{ status.label }}
          </button>
        </div>
      </div>

      <el-empty v-if="!orders.length" description="暂无订单" />

      <template v-else>
        <article
          v-for="order in orders"
          :key="order.id"
          class="order-row order-row--interactive"
          role="link"
          tabindex="0"
          @click="openFirstProduct(order)"
          @keydown.enter.prevent="openFirstProduct(order)"
        >
          <div class="order-row__main">
            <div class="order-identity">
              <span>订单号</span>
              <strong>{{ order.orderNo }}</strong>
              <small>{{ order.createdAt }}</small>
            </div>

            <div class="order-product-line">
              <img
                :src="firstItem(order)?.productImage"
                :alt="firstItem(order)?.productName || '商品'"
              />
              <div>
                <strong>{{ firstItem(order)?.productName || '商品' }}</strong>
                <small>{{ productSummary(order) }}</small>
              </div>
            </div>

            <strong class="order-total">¥{{ formatMoney(order.totalAmount) }}</strong>

            <span class="order-status-badge" :class="`order-status-badge--${order.status.toLowerCase()}`">
              {{ statusLabel(order.status) }}
            </span>
          </div>

          <div class="order-actions" @click.stop>
            <el-button class="order-action-button" size="small" @click.stop="router.push(`/orders/${order.id}`)">详情</el-button>
            <el-button
              v-if="order.status === 'CREATED'"
              class="order-action-button order-action-button--primary"
              size="small"
              :loading="isBusy(order.id, 'pay')"
              :disabled="isAnyBusy(order.id)"
              @click.stop="pay(order.id)"
            >
              支付
            </el-button>
            <el-button
              v-if="canCancel(order.status)"
              class="order-action-button order-action-button--danger"
              size="small"
              :loading="isBusy(order.id, 'cancel')"
              :disabled="isAnyBusy(order.id)"
              @click.stop="cancel(order.id)"
            >
              取消
            </el-button>
            <el-button
              v-if="order.status === 'SHIPPED'"
              class="order-action-button order-action-button--success"
              size="small"
              :loading="isBusy(order.id, 'receive')"
              :disabled="isAnyBusy(order.id)"
              @click.stop="receive(order.id)"
            >
              确认收货
            </el-button>
          </div>
        </article>
      </template>

      <el-pagination
        class="store-pagination"
        layout="prev, pager, next"
        :current-page="query.page"
        :page-size="query.size"
        :total="total"
        @current-change="handlePageChange"
      />
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cancelOrder, getOrders, payOrder, receiveOrder } from '../api/orders'
import type { Order, OrderItem, OrderStatus } from '../types/order'
import type { EntityId } from '../types/product'

const router = useRouter()
const orders = ref<Order[]>([])
const total = ref(0)
const busyActions = ref(new Set<string>())
const query = reactive({
  page: 1,
  size: 8,
  status: null as OrderStatus | null
})

const statusOptions: Array<{ label: string; value: OrderStatus }> = [
  { label: '待支付', value: 'CREATED' },
  { label: '已支付', value: 'PAID' },
  { label: '已发货', value: 'SHIPPED' },
  { label: '已收货', value: 'RECEIVED' },
  { label: '已取消', value: 'CANCELLED' }
]

const statusFilters: Array<{ label: string; value: OrderStatus | null }> = [
  { label: '全部', value: null },
  ...statusOptions
]

function statusLabel(status: OrderStatus) {
  return statusOptions.find((item) => item.value === status)?.label || status
}

function canCancel(status: OrderStatus) {
  return status === 'CREATED' || status === 'PAID'
}

function firstItem(order: Order): OrderItem | undefined {
  return order.items[0]
}

function productSummary(order: Order) {
  const totalQuantity = order.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0)
  if (order.items.length > 1) {
    return `等 ${order.items.length} 件 · 共 ${totalQuantity} 件`
  }
  return `共 ${totalQuantity || 1} 件`
}

function openFirstProduct(order: Order) {
  const productId = firstItem(order)?.productId
  if (productId) {
    router.push(`/products/${productId}`)
  }
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
  return ['pay', 'cancel', 'receive'].some((action) => isBusy(id, action))
}

async function loadOrders() {
  try {
    const page = await getOrders(query)
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

function setStatus(status: OrderStatus | null) {
  query.status = status
  reload()
}

async function pay(id: EntityId) {
  setBusy(id, 'pay', true)
  try {
    await payOrder(id)
    ElMessage.success('支付成功')
    await loadOrders()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '支付失败')
  } finally {
    setBusy(id, 'pay', false)
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
    await cancelOrder(id)
    ElMessage.success('订单已取消')
    await loadOrders()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '取消订单失败')
  } finally {
    setBusy(id, 'cancel', false)
  }
}

async function receive(id: EntityId) {
  setBusy(id, 'receive', true)
  try {
    await receiveOrder(id)
    ElMessage.success('已确认收货')
    await loadOrders()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '确认收货失败')
  } finally {
    setBusy(id, 'receive', false)
  }
}

function handlePageChange(page: number) {
  query.page = page
  loadOrders()
}

onMounted(loadOrders)
</script>
