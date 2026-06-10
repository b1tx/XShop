<template>
  <main class="admin-shell">
    <aside class="sidebar">
      <h1>AI 电商后台</h1>
      <RouterLink class="active" to="/admin">销售看板</RouterLink>
      <RouterLink to="/admin/products">商品管理</RouterLink>
      <RouterLink to="/admin/orders">订单管理</RouterLink>
      <a>促销管理</a>
      <RouterLink to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/">返回店铺</RouterLink>
    </aside>

    <section class="admin-content">
      <header class="admin-header">
        <div>
          <p class="eyebrow">Operations</p>
          <h2>销售看板</h2>
        </div>
        <el-button type="primary">新增商品</el-button>
      </header>

      <section class="metrics">
        <article v-for="metric in metrics" :key="metric.label" class="metric">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
        </article>
      </section>

      <section class="table-panel">
        <div class="section-title">
          <span>库存预警</span>
          <el-tag type="warning">8 个商品</el-tag>
        </div>
        <el-table :data="lowStockProducts" style="width: 100%">
          <el-table-column prop="name" label="商品" />
          <el-table-column prop="stock" label="库存" width="120" />
          <el-table-column prop="status" label="状态" width="120" />
        </el-table>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
const metrics = [
  { label: '今日销售额', value: '¥12,800' },
  { label: '订单数', value: '64' },
  { label: '支付订单', value: '51' },
  { label: '低库存', value: '8' }
]

const lowStockProducts = [
  { name: '轻薄笔记本 Pro 14', stock: 6, status: '需补货' },
  { name: '无线降噪耳机 Air', stock: 9, status: '需关注' },
  { name: '人体工学办公椅', stock: 4, status: '需补货' }
]
</script>
