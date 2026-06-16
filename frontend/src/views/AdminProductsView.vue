<template>
  <main class="admin-shell">
    <aside class="sidebar">
      <h1>AI 电商后台</h1>
      <RouterLink to="/admin">销售看板</RouterLink>
      <RouterLink class="active" to="/admin/products">商品管理</RouterLink>
      <RouterLink to="/admin/orders">订单管理</RouterLink>
      <RouterLink to="/admin/promotions">促销管理</RouterLink>
      <RouterLink to="/admin/ai-operation">AI 运营助手</RouterLink>
      <RouterLink to="/admin/users">用户管理</RouterLink>
      <RouterLink to="/">返回店铺</RouterLink>
    </aside>

    <section class="admin-content">
      <header class="admin-header">
        <div>
          <p class="eyebrow">Products</p>
          <h2>商品管理</h2>
        </div>
        <div class="admin-actions">
          <el-button @click="categoryDialogVisible = true">新增分类</el-button>
          <el-button type="primary" @click="openCreate">新增商品</el-button>
        </div>
      </header>

      <section class="table-panel">
        <div class="admin-filter">
          <el-input v-model="query.keyword" clearable placeholder="搜索商品" />
          <el-select v-model="query.categoryId" clearable placeholder="分类">
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
          <el-select v-model="query.status" clearable placeholder="状态">
            <el-option label="上架" :value="1" />
            <el-option label="下架" :value="0" />
          </el-select>
          <el-button type="primary" @click="loadProducts">查询</el-button>
        </div>

        <el-table :data="products" style="width: 100%">
          <el-table-column label="商品" min-width="260">
            <template #default="{ row }">
              <div class="admin-product-cell">
                <img :src="row.mainImage" :alt="row.name" />
                <div>
                  <strong>{{ row.name }}</strong>
                  <span>{{ row.subtitle }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="categoryName" label="分类" width="100" />
          <el-table-column prop="price" label="价格" width="100" />
          <el-table-column prop="stock" label="库存" width="90" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '上架' : '下架' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" @click="toggleStatus(row)">{{ row.status === 1 ? '下架' : '上架' }}</el-button>
              <el-button size="small" type="danger" @click="removeProduct(row.id)">删除</el-button>
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

    <el-dialog v-model="productDialogVisible" :title="editingProduct ? '编辑商品' : '新增商品'" width="720px">
      <el-form :model="productForm" label-width="90px">
        <el-form-item label="分类">
          <el-select v-model="productForm.categoryId" placeholder="选择分类">
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="productForm.name" />
        </el-form-item>
        <el-form-item label="副标题">
          <el-input v-model="productForm.subtitle" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="productForm.price" :min="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="productForm.stock" :min="0" />
        </el-form-item>
        <el-form-item label="商品图片">
          <div class="product-image-upload">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              accept="image/jpeg,image/png,image/webp"
              :on-change="handleImageSelected"
            >
              <el-button :loading="imageUploading">选择本地图片</el-button>
            </el-upload>
            <span>支持 jpg、png、webp，不超过 5MB</span>
            <div v-if="productForm.mainImage" class="product-image-preview">
              <img :src="productForm.mainImage" alt="商品图片预览" />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="详情">
          <el-input v-model="productForm.detail" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="productForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="imageUploading" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="categoryDialogVisible" title="新增分类" width="420px">
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadFile } from 'element-plus'
import {
  createAdminCategory,
  createAdminProduct,
  deleteAdminProduct,
  getAdminCategories,
  getAdminProducts,
  updateAdminProduct,
  updateAdminProductStatus
} from '../api/admin'
import { uploadProductImage } from '../api/uploads'
import type { Category, EntityId, Product, ProductPayload } from '../types/product'

const products = ref<Product[]>([])
const categories = ref<Category[]>([])
const total = ref(0)
const productDialogVisible = ref(false)
const categoryDialogVisible = ref(false)
const editingProduct = ref<Product | null>(null)
const imageUploading = ref(false)

const query = reactive({
  page: 1,
  size: 10,
  keyword: '',
  categoryId: null as EntityId | null,
  status: null as number | null
})

const productForm = reactive<ProductPayload>({
  categoryId: 0,
  name: '',
  subtitle: '',
  price: 0,
  stock: 0,
  mainImage: '',
  detail: '',
  status: 1
})

const categoryForm = reactive({
  name: '',
  sort: 0,
  status: 1
})

async function loadCategories() {
  categories.value = await getAdminCategories()
}

async function loadProducts() {
  const page = await getAdminProducts(query)
  products.value = page.records
  total.value = page.total
}

function resetProductForm() {
  productForm.categoryId = categories.value[0]?.id || 0
  productForm.name = ''
  productForm.subtitle = ''
  productForm.price = 0
  productForm.stock = 0
  productForm.mainImage = ''
  productForm.detail = ''
  productForm.status = 1
}

function openCreate() {
  editingProduct.value = null
  resetProductForm()
  productDialogVisible.value = true
}

function openEdit(product: Product) {
  editingProduct.value = product
  productForm.categoryId = product.categoryId
  productForm.name = product.name
  productForm.subtitle = product.subtitle
  productForm.price = product.price
  productForm.stock = product.stock
  productForm.mainImage = product.mainImage
  productForm.detail = product.detail
  productForm.status = product.status
  productDialogVisible.value = true
}

async function saveProduct() {
  if (!productForm.mainImage) {
    ElMessage.warning('请先上传商品图片')
    return
  }
  if (editingProduct.value) {
    await updateAdminProduct(editingProduct.value.id, productForm)
  } else {
    await createAdminProduct(productForm)
  }
  ElMessage.success('保存成功')
  productDialogVisible.value = false
  await loadProducts()
}

async function handleImageSelected(uploadFile: UploadFile) {
  const rawFile = uploadFile.raw
  if (!rawFile) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(rawFile.type)) {
    ElMessage.warning('仅支持 jpg、png、webp 图片')
    return
  }
  if (rawFile.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 5MB')
    return
  }

  imageUploading.value = true
  try {
    const result = await uploadProductImage(rawFile)
    productForm.mainImage = result.url
    ElMessage.success('图片上传成功')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '图片上传失败')
  } finally {
    imageUploading.value = false
  }
}

async function toggleStatus(product: Product) {
  await updateAdminProductStatus(product.id, product.status === 1 ? 0 : 1)
  ElMessage.success('状态已更新')
  await loadProducts()
}

async function removeProduct(id: EntityId) {
  await ElMessageBox.confirm('确认删除该商品？', '删除商品')
  await deleteAdminProduct(id)
  ElMessage.success('删除成功')
  await loadProducts()
}

async function saveCategory() {
  await createAdminCategory(categoryForm)
  ElMessage.success('分类已创建')
  categoryDialogVisible.value = false
  categoryForm.name = ''
  categoryForm.sort = 0
  await loadCategories()
}

function handlePageChange(page: number) {
  query.page = page
  loadProducts()
}

onMounted(async () => {
  await loadCategories()
  await loadProducts()
})
</script>
