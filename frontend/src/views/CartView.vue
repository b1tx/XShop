<template>
  <main class="store-shell gothic-store">
    <header class="gothic-header">
      <div class="store-container gothic-header__inner detail-header">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>夜幕商店</strong>
            <small>Cart</small>
          </span>
        </RouterLink>
        <div class="gothic-actions">
          <RouterLink to="/">继续选购</RouterLink>
          <RouterLink to="/orders">我的订单</RouterLink>
        </div>
      </div>
    </header>

    <section class="store-container cart-layout">
      <div class="cart-heading">
        <div>
          <p class="eyebrow">Selected Goods</p>
          <h1>购物车</h1>
        </div>
        <el-button text @click="loadItems({ preserveSelection: true })">刷新</el-button>
      </div>

      <el-empty v-if="!items.length" description="购物车暂无商品">
        <el-button type="primary" @click="$router.push('/')">浏览商品</el-button>
      </el-empty>

      <template v-else>
        <el-checkbox-group v-model="selectedIds" class="cart-items">
          <article v-for="item in items" :key="item.id" class="cart-row">
            <el-checkbox :value="item.id" @click.stop />
            <div class="cart-row__product">
              <RouterLink class="cart-row__image-link" :to="`/products/${item.productId}`" @click.stop>
                <img :src="item.mainImage" :alt="cartProductName(item)" />
              </RouterLink>
              <div class="cart-row__info">
                <RouterLink class="cart-row__title" :to="`/products/${item.productId}`" @click.stop>
                  {{ cartProductName(item) }}
                </RouterLink>
                <span>{{ item.subtitle || '暂无商品副标题' }}</span>
                <small>库存 {{ item.stock }}</small>
              </div>
            </div>
            <strong>¥{{ formatMoney(item.price) }}</strong>
            <div class="cart-row__quantity" @click.stop>
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="item.stock"
                :disabled="updatingItemIds.has(item.id) || deletingItemIds.has(item.id)"
                size="small"
                @change="(value: number | undefined) => changeQuantity(item, Number(value || 1))"
              />
            </div>
            <strong>¥{{ formatMoney(itemSubtotal(item)) }}</strong>
            <el-button
              text
              type="danger"
              :loading="deletingItemIds.has(item.id)"
              :disabled="updatingItemIds.has(item.id)"
              @click.stop="removeItem(item.id)"
            >
              删除
            </el-button>
          </article>
        </el-checkbox-group>

        <footer class="cart-summary">
          <span>已选 {{ selectedItems.length }} 件</span>
          <strong>合计 ¥{{ formatMoney(totalAmount) }}</strong>
          <el-button type="primary" size="large" @click="openCheckout">
            去结算
          </el-button>
        </footer>
      </template>
    </section>

    <el-dialog
      v-model="checkoutVisible"
      class="gothic-dialog"
      width="min(560px, calc(100vw - 32px))"
      append-to-body
    >
      <template #header>
        <div class="gothic-dialog__intro">
          <p class="eyebrow">Checkout</p>
          <h2>填写收货信息</h2>
          <span>确认收货信息后，将为已选商品创建订单。</span>
        </div>
      </template>

      <div class="gothic-dialog__summary gothic-dialog__summary--compact">
        <div>
          <strong>已选 {{ selectedItems.length }} 件商品</strong>
          <span>{{ selectedItemsSummary }}</span>
          <em>合计 ¥{{ formatMoney(totalAmount) }}</em>
        </div>
      </div>

      <el-form class="gothic-form-grid" :model="checkoutForm" label-position="top">
        <el-form-item label="收货人">
          <el-input v-model="checkoutForm.receiverName" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="checkoutForm.receiverPhone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="checkoutForm.receiverAddress" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkoutVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitOrder">提交订单</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteCartItem, getCartItems, updateCartItemQuantity } from '../api/cart'
import { createOrder } from '../api/orders'
import { useAuthStore } from '../stores/auth'
import type { CartItem } from '../types/cart'
import type { EntityId } from '../types/product'

const router = useRouter()
const authStore = useAuthStore()
const items = ref<CartItem[]>([])
const selectedIds = ref<EntityId[]>([])
const checkoutVisible = ref(false)
const submitting = ref(false)
const updatingItemIds = ref(new Set<EntityId>())
const deletingItemIds = ref(new Set<EntityId>())

const checkoutForm = reactive({
  receiverName: authStore.user?.nickname || '',
  receiverPhone: authStore.user?.phone || '',
  receiverAddress: ''
})

const selectedItems = computed(() => items.value.filter((item) => selectedIds.value.includes(item.id)))
const totalAmount = computed(() => selectedItems.value.reduce((sum, item) => sum + itemSubtotal(item), 0))
const selectedItemsSummary = computed(() => {
  if (!selectedItems.value.length) return '暂无选中商品'
  const first = cartProductName(selectedItems.value[0])
  return selectedItems.value.length > 1 ? `${first} 等 ${selectedItems.value.length} 件` : first
})

function formatMoney(value: number) {
  return Number(value || 0).toFixed(2)
}

function itemSubtotal(item: CartItem) {
  return Number(item.price || 0) * Number(item.quantity || 0)
}

function cartProductName(item: CartItem) {
  return item.productName?.trim() || '查看商品详情'
}

function setBusy(target: typeof updatingItemIds, id: EntityId, busy: boolean) {
  const next = new Set(target.value)
  if (busy) {
    next.add(id)
  } else {
    next.delete(id)
  }
  target.value = next
}

function syncSelectedIds(nextItems: CartItem[], preserveSelection: boolean) {
  if (!preserveSelection) {
    selectedIds.value = nextItems.map((item) => item.id)
    return
  }
  const validIds = new Set(nextItems.map((item) => item.id))
  selectedIds.value = selectedIds.value.filter((id) => validIds.has(id))
}

async function loadItems(options: { preserveSelection?: boolean } = {}) {
  try {
    const nextItems = await getCartItems()
    items.value = nextItems
    syncSelectedIds(nextItems, Boolean(options.preserveSelection))
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '购物车加载失败')
  }
}

async function changeQuantity(item: CartItem, quantity: number) {
  const previousQuantity = item.quantity
  const nextQuantity = Math.max(1, Math.min(quantity, item.stock))
  item.quantity = nextQuantity
  setBusy(updatingItemIds, item.id, true)
  try {
    const updated = await updateCartItemQuantity(item.id, nextQuantity)
    Object.assign(item, updated)
    ElMessage.success('数量已更新')
  } catch (error) {
    item.quantity = previousQuantity
    ElMessage.error(error instanceof Error ? error.message : '数量修改失败')
  } finally {
    setBusy(updatingItemIds, item.id, false)
  }
}

async function removeItem(id: EntityId) {
  try {
    await ElMessageBox.confirm('确认从购物车删除该商品？', '删除商品')
  } catch {
    return
  }
  setBusy(deletingItemIds, id, true)
  try {
    await deleteCartItem(id)
    items.value = items.value.filter((item) => item.id !== id)
    selectedIds.value = selectedIds.value.filter((selectedId) => selectedId !== id)
    ElMessage.success('已删除')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '删除失败')
  } finally {
    setBusy(deletingItemIds, id, false)
  }
}

function openCheckout() {
  if (!selectedItems.value.length) {
    ElMessage.warning('请先选择要结算的商品')
    return
  }
  checkoutVisible.value = true
}

async function submitOrder() {
  if (!checkoutForm.receiverName || !checkoutForm.receiverPhone || !checkoutForm.receiverAddress) {
    ElMessage.warning('请完整填写收货信息')
    return
  }
  const cartItemIds = selectedItems.value.map((item) => item.id)
  if (!cartItemIds.length) {
    ElMessage.warning('请先选择要结算的商品')
    return
  }
  submitting.value = true
  try {
    const order = await createOrder({
      cartItemIds,
      receiverName: checkoutForm.receiverName,
      receiverPhone: checkoutForm.receiverPhone,
      receiverAddress: checkoutForm.receiverAddress
    })
    ElMessage.success('订单已创建')
    checkoutVisible.value = false
    router.push(`/orders/${order.id}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '订单创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadItems)
</script>
