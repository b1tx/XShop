<template>
  <main class="store-shell gothic-store">
    <header class="gothic-header">
      <div class="store-container gothic-header__inner detail-header">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>夜幕商店</strong>
            <small>Product Detail</small>
          </span>
        </RouterLink>
        <div class="gothic-actions">
          <RouterLink to="/products">返回商品列表</RouterLink>
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
        <el-button type="primary" size="large">加入购物车</el-button>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getProductDetail } from '../api/products'
import type { Product } from '../types/product'

const route = useRoute()
const product = ref<Product | null>(null)

onMounted(async () => {
  product.value = await getProductDetail(Number(route.params.id))
})
</script>

