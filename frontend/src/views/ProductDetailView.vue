<template>
  <main class="store-shell gothic-store">
    <header class="gothic-header">
      <div class="store-container gothic-header__inner detail-header">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>XSHOP</strong>
            <small>Product Detail</small>
          </span>
        </RouterLink>
        <div class="gothic-actions">
          <RouterLink to="/">返回店铺</RouterLink>
          <RouterLink to="/cart">购物车</RouterLink>
          <RouterLink to="/orders">订单</RouterLink>
        </div>
      </div>
    </header>

    <section v-if="product" class="store-container detail-layout">
      <div class="detail-image">
        <img :src="product.mainImage" :alt="product.name" />
      </div>
      <div class="detail-info">
        <p class="eyebrow">{{ product.categoryName }}</p>
        <h1>{{ product.name }}</h1>
        <p>{{ product.subtitle }}</p>
        <strong>¥{{ product.price }}</strong>
        <div class="detail-meta">
          <span>库存 {{ product.stock }}</span>
          <span>{{ product.status === 1 ? '已上架' : '已下架' }}</span>
        </div>
        <div class="detail-copy">{{ product.detail }}</div>
        <div class="detail-cart-action">
          <el-input-number v-model="quantity" :min="1" :max="product.stock" />
          <el-button type="primary" size="large" :disabled="product.stock <= 0" @click="addToCart">
            加入购物车
          </el-button>
        </div>

        <section class="product-ai-panel">
          <div>
            <p class="eyebrow">Product Q&A</p>
            <h2>AI 商品问答</h2>
            <span>围绕场景、材质、搭配或使用方式提问。</span>
          </div>
          <div class="product-ai-panel__ask">
            <el-input
              v-model="aiQuestion"
              type="textarea"
              :rows="3"
              placeholder="例如：这件商品适合什么场景？材质和搭配有什么建议？"
            />
            <el-button type="primary" :loading="aiLoading" @click="askProduct">
              询问 AI
            </el-button>
          </div>
          <div v-if="aiAnswer" class="ai-result-panel product-ai-answer">
            <strong>AI 回答</strong>
            <span>{{ aiAnswer }}</span>
          </div>
        </section>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { productQa } from '../api/ai'
import { addCartItem } from '../api/cart'
import { getProductDetail } from '../api/products'
import { useAuthStore } from '../stores/auth'
import type { Product } from '../types/product'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const product = ref<Product | null>(null)
const quantity = ref(1)
const aiQuestion = ref('')
const aiAnswer = ref('')
const aiLoading = ref(false)

async function addToCart() {
  if (!product.value) return
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后加入购物车')
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  await addCartItem({ productId: product.value.id, quantity: quantity.value })
  ElMessage.success('已加入购物车')
}

async function askProduct() {
  if (!product.value) return
  if (!aiQuestion.value.trim()) {
    ElMessage.warning('请输入你的问题')
    return
  }
  aiLoading.value = true
  try {
    const result = await productQa(product.value.id, aiQuestion.value.trim())
    aiAnswer.value = result.content
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : 'AI 问答暂不可用')
  } finally {
    aiLoading.value = false
  }
}

onMounted(async () => {
  product.value = await getProductDetail(String(route.params.id))
})
</script>
