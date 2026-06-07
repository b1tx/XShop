<template>
  <main class="store-shell gothic-store">
    <header class="gothic-header">
      <div class="store-container gothic-header__inner">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>夜幕商店</strong>
            <small>Products</small>
          </span>
        </RouterLink>
        <div class="gothic-search">
          <el-input v-model="query.keyword" placeholder="搜索商品" clearable @keyup.enter="loadProducts" />
        </div>
        <nav class="gothic-nav">
          <button
            v-for="category in categoryOptions"
            :key="category.id"
            :class="{ active: (query.categoryId || 0) === category.id }"
            type="button"
            @click="switchCategory(category.id)"
          >
            {{ category.name }}
          </button>
        </nav>
        <div class="gothic-actions">
          <RouterLink to="/">首页</RouterLink>
          <RouterLink to="/login">登录</RouterLink>
        </div>
      </div>
    </header>

    <section class="store-container product-section gothic-products">
      <div class="product-toolbar">
        <div>
          <p class="eyebrow">Catalog</p>
          <h2>商品列表</h2>
        </div>
        <div class="toolbar-controls">
          <el-button type="primary" @click="loadProducts">搜索</el-button>
          <div class="view-switch">
            <span>视图</span>
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button value="compact">紧凑</el-radio-button>
              <el-radio-button value="comfortable">标准</el-radio-button>
              <el-radio-button value="large">大图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </div>

      <div class="product-grid" :class="`product-grid--${viewMode}`">
        <article v-for="product in products" :key="product.id" class="product-card">
          <div class="product-image-frame">
            <img :src="product.mainImage" :alt="product.name" loading="lazy" />
            <em>{{ product.categoryName }}</em>
          </div>
          <div class="product-info">
            <div class="product-price">
              <strong>¥{{ product.price }}</strong>
              <span>库存 {{ product.stock }}</span>
            </div>
            <RouterLink :to="`/products/${product.id}`">
              <h3>{{ product.name }}</h3>
            </RouterLink>
            <p>{{ product.subtitle }}</p>
            <button type="button">加入购物车</button>
          </div>
        </article>
      </div>

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
import { getCategories, getProducts } from '../api/products'
import type { Category, Product } from '../types/product'

type ViewMode = 'compact' | 'comfortable' | 'large'

const viewMode = ref<ViewMode>('comfortable')
const products = ref<Product[]>([])
const total = ref(0)
const categoryOptions = ref<Array<Pick<Category, 'id' | 'name'>>>([{ id: 0, name: '全部' }])
const query = reactive({
  page: 1,
  size: 8,
  keyword: '',
  categoryId: null as number | null
})

async function loadProducts() {
  const page = await getProducts(query)
  products.value = page.records
  total.value = page.total
}

function switchCategory(id: number) {
  query.categoryId = id === 0 ? null : id
  query.page = 1
  loadProducts()
}

function handlePageChange(page: number) {
  query.page = page
  loadProducts()
}

onMounted(async () => {
  const categories = await getCategories()
  categoryOptions.value = [{ id: 0, name: '全部' }, ...categories.map((category) => ({ id: category.id, name: category.name }))]
  await loadProducts()
})
</script>

