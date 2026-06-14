<template>
  <main class="admin-shell">
    <aside class="sidebar">
      <h1>AI 电商后台</h1>
      <RouterLink to="/admin">销售看板</RouterLink>
      <RouterLink to="/admin/products">商品管理</RouterLink>
      <RouterLink to="/admin/orders">订单管理</RouterLink>
      <RouterLink to="/admin/promotions">促销管理</RouterLink>
      <RouterLink class="active" to="/admin/ai-operation">AI 运营助手</RouterLink>
      <RouterLink to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/">返回店铺</RouterLink>
    </aside>

    <section class="admin-content">
      <header class="admin-header">
        <div>
          <p class="eyebrow">AI Operation</p>
          <h2>AI 运营助手</h2>
        </div>
      </header>

      <section class="ai-operation-grid">
        <article class="table-panel ai-operation-card">
          <div class="section-title">
            <div>
              <span>商品文案生成</span>
              <p>根据商品名、卖点和目标用户生成前台展示文案。</p>
            </div>
          </div>
          <el-form label-position="top">
            <el-form-item label="商品名">
              <el-input v-model="copyForm.productName" />
            </el-form-item>
            <el-form-item label="卖点">
              <el-input v-model="sellingPointsText" placeholder="用逗号分隔，例如：黑色、复古、银饰" />
            </el-form-item>
            <el-form-item label="目标用户">
              <el-input v-model="copyForm.targetUser" />
            </el-form-item>
          </el-form>
          <el-button type="primary" :loading="copyLoading" @click="generateCopy">生成文案</el-button>
          <div v-if="copyResult" class="ai-operation-result">
            <strong>生成结果</strong>
            <p>{{ copyResult }}</p>
          </div>
        </article>

        <article class="table-panel ai-operation-card">
          <div class="section-title">
            <div>
              <span>运营分析</span>
              <p>汇总近期经营情况，输出销售、库存和补货建议。</p>
            </div>
          </div>
          <el-form label-position="top">
            <el-form-item label="时间范围">
              <el-select v-model="analysisForm.dateRange">
                <el-option label="近 7 天" value="LAST_7_DAYS" />
                <el-option label="近 30 天" value="LAST_30_DAYS" />
              </el-select>
            </el-form-item>
            <el-form-item label="关注点">
              <el-input v-model="analysisForm.focus" />
            </el-form-item>
          </el-form>
          <el-button type="primary" :loading="analysisLoading" @click="analyze">生成分析</el-button>
          <div v-if="analysisResult" class="ai-operation-result">
            <strong>分析结果</strong>
            <p>{{ analysisResult }}</p>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { operationAnalysis, productCopywriting } from '../api/ai'

const sellingPointsText = ref('黑色质感, 复古轮廓, 易搭配')
const copyLoading = ref(false)
const analysisLoading = ref(false)
const copyResult = ref('')
const analysisResult = ref('')

const copyForm = reactive({
  productName: '黑曜短斗篷外套',
  targetUser: '喜欢哥特风穿搭的年轻用户'
})

const analysisForm = reactive({
  dateRange: 'LAST_7_DAYS',
  focus: '库存补货建议'
})

async function generateCopy() {
  copyLoading.value = true
  try {
    const result = await productCopywriting({
      productName: copyForm.productName,
      sellingPoints: sellingPointsText.value.split(/[,，]/).map((item) => item.trim()).filter(Boolean),
      targetUser: copyForm.targetUser
    })
    copyResult.value = result.content
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '文案生成失败')
  } finally {
    copyLoading.value = false
  }
}

async function analyze() {
  analysisLoading.value = true
  try {
    const result = await operationAnalysis(analysisForm.dateRange, analysisForm.focus)
    analysisResult.value = result.content
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '运营分析失败')
  } finally {
    analysisLoading.value = false
  }
}
</script>
