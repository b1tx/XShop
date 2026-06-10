<template>
  <main class="store-shell gothic-store">
    <header class="gothic-header">
      <div class="store-container gothic-header__inner detail-header">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>夜幕商店</strong>
            <small>Order Detail</small>
          </span>
        </RouterLink>
        <div class="gothic-actions">
          <RouterLink to="/orders">我的订单</RouterLink>
          <RouterLink to="/cart">购物车</RouterLink>
        </div>
      </div>
    </header>

    <section v-if="order" class="store-container order-detail">
      <div class="order-detail__hero">
        <div>
          <p class="eyebrow">Order {{ order.orderNo }}</p>
          <h1>{{ statusLabel(order.status) }}</h1>
          <span>{{ order.receiverName }} · {{ order.receiverPhone }} · {{ order.receiverAddress }}</span>
        </div>
        <strong>¥{{ formatMoney(order.totalAmount) }}</strong>
      </div>

      <div class="order-detail__actions">
        <el-button v-if="order.status === 'CREATED'" type="primary" :loading="actionLoading === 'pay'" :disabled="Boolean(actionLoading)" @click="pay">
          模拟支付
        </el-button>
        <el-button v-if="canCancel(order.status)" type="danger" :loading="actionLoading === 'cancel'" :disabled="Boolean(actionLoading)" @click="cancel">
          取消订单
        </el-button>
        <el-button v-if="order.status === 'SHIPPED'" type="success" :loading="actionLoading === 'receive'" :disabled="Boolean(actionLoading)" @click="receive">
          确认收货
        </el-button>
      </div>

      <section class="order-items-panel">
        <article v-for="item in order.items" :key="item.id" class="cart-row order-item-row">
          <img :src="item.productImage" :alt="item.productName" />
          <div class="cart-row__info">
            <RouterLink :to="`/products/${item.productId}`">{{ item.productName }}</RouterLink>
            <small>数量 {{ item.quantity }}</small>
          </div>
          <strong>¥{{ formatMoney(item.price) }}</strong>
          <strong>¥{{ formatMoney(item.totalAmount) }}</strong>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cancelOrder, getOrderDetail, payOrder, receiveOrder } from '../api/orders'
import type { Order, OrderStatus } from '../types/order'

const route = useRoute()
const order = ref<Order | null>(null)
const actionLoading = ref<'pay' | 'cancel' | 'receive' | ''>('')

const labels: Record<OrderStatus, string> = {
  CREATED: '待支付',
  PAID: '已支付',
  SHIPPED: '已发货',
  RECEIVED: '已收货',
  CANCELLED: '已取消'
}

function statusLabel(status: OrderStatus) {
  return labels[status]
}

function canCancel(status: OrderStatus) {
  return status === 'CREATED' || status === 'PAID'
}

function formatMoney(value: number) {
  return Number(value || 0).toFixed(2)
}

async function loadOrder() {
  try {
    order.value = await getOrderDetail(String(route.params.id))
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '订单加载失败')
  }
}

async function pay() {
  if (!order.value) return
  actionLoading.value = 'pay'
  try {
    order.value = await payOrder(order.value.id)
    ElMessage.success('支付成功')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '支付失败')
  } finally {
    actionLoading.value = ''
  }
}

async function cancel() {
  if (!order.value) return
  try {
    await ElMessageBox.confirm('确认取消该订单？库存会自动回滚。', '取消订单')
  } catch {
    return
  }
  actionLoading.value = 'cancel'
  try {
    order.value = await cancelOrder(order.value.id)
    ElMessage.success('订单已取消')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '取消订单失败')
  } finally {
    actionLoading.value = ''
  }
}

async function receive() {
  if (!order.value) return
  actionLoading.value = 'receive'
  try {
    order.value = await receiveOrder(order.value.id)
    ElMessage.success('已确认收货')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '确认收货失败')
  } finally {
    actionLoading.value = ''
  }
}

onMounted(loadOrder)
</script>
