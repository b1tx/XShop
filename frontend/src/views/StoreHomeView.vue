<template>
  <main class="store-shell">
    <header class="store-header">
      <div>
        <p class="eyebrow">B2C AI Commerce</p>
        <h1>智能导购商城</h1>
      </div>
      <nav class="store-nav">
        <RouterLink to="/">商城首页</RouterLink>
        <RouterLink to="/admin">后台看板</RouterLink>
      </nav>
    </header>

    <section class="store-workspace">
      <div class="catalog-panel">
        <div class="section-title">
          <span>商品列表</span>
          <el-button type="primary">AI 导购</el-button>
        </div>
        <div class="product-grid">
          <article v-for="product in products" :key="product.name" class="product-row">
            <div>
              <h2>{{ product.name }}</h2>
              <p>{{ product.subtitle }}</p>
            </div>
            <strong>¥{{ product.price }}</strong>
          </article>
        </div>
      </div>

      <aside class="assistant-panel">
        <p class="eyebrow">AI Guide</p>
        <h2>根据预算和用途生成购买建议</h2>
        <el-input
          v-model="question"
          type="textarea"
          :rows="5"
          placeholder="例如：预算 5000，适合学生的轻薄笔记本"
        />
        <el-button type="primary">生成建议</el-button>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const question = ref('')

const products = [
  { name: '轻薄笔记本 Pro 14', subtitle: '16GB 内存，长续航，适合学习和办公', price: '4999' },
  { name: '无线降噪耳机 Air', subtitle: '通勤降噪，低延迟连接', price: '699' },
  { name: '人体工学办公椅', subtitle: '腰背支撑，适合长时间办公', price: '1299' }
]
</script>

