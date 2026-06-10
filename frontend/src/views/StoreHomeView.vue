<template>
  <main class="store-shell gothic-store">
    <div class="gothic-userbar">
      <div class="store-container userbar-inner">
        <div v-if="authStore.isLoggedIn && authStore.user" class="userbar-status">
          <span>当前用户：{{ authStore.user.nickname }}（{{ authStore.user.username }}）</span>
          <span class="role-badge">角色：{{ roleLabel }}</span>
        </div>
        <div v-else class="userbar-status">
          <span>游客模式</span>
          <span class="role-badge">未登录</span>
        </div>

        <div class="userbar-links">
          <template v-if="authStore.isLoggedIn">
            <RouterLink v-if="authStore.isAdmin" to="/admin/products">进入后台</RouterLink>
            <button type="button" @click="handleLogout">退出登录</button>
          </template>
          <template v-else>
            <RouterLink to="/login">登录</RouterLink>
            <RouterLink to="/register">注册</RouterLink>
          </template>
        </div>
      </div>
    </div>

    <header class="gothic-header">
      <div class="store-container gothic-header__inner">
        <RouterLink class="gothic-brand" to="/">
          <span class="gothic-brand__mark">N</span>
          <span>
            <strong>夜幕商店</strong>
            <small>Nocturne Atelier</small>
          </span>
        </RouterLink>

        <div class="gothic-search">
          <el-icon><Search /></el-icon>
          <input v-model="searchKeyword" placeholder="搜索斗篷、银饰、香氛" />
        </div>

        <nav class="gothic-nav">
          <button
            v-for="category in categories"
            :key="category.id"
            :class="{ active: (activeCategoryId || 0) === category.id }"
            type="button"
            @click="switchCategory(category.id)"
          >
            {{ category.name }}
          </button>
        </nav>

        <div class="gothic-actions">
          <RouterLink to="/admin">后台</RouterLink>
          <button type="button" @click="goCart">
            <el-icon><ShoppingCart /></el-icon>
            购物车
          </button>
        </div>
      </div>
    </header>

    <section class="gothic-hero">
      <el-carousel height="520px" trigger="click" arrow="always" indicator-position="outside">
        <el-carousel-item v-for="slide in heroSlides" :key="slide.title">
          <article class="hero-slide">
            <img :src="slide.image" :alt="slide.title" />
            <div class="hero-slide__shade"></div>
            <div class="store-container hero-slide__content">
              <p class="eyebrow">{{ slide.kicker }}</p>
              <h1>{{ slide.title }}</h1>
              <p>{{ slide.description }}</p>
              <div class="hero-actions">
                <el-button type="primary" size="large">进入系列</el-button>
                <el-button size="large" plain>查看新品</el-button>
              </div>
            </div>
          </article>
        </el-carousel-item>
      </el-carousel>
    </section>

    <section class="store-container product-section gothic-products">
      <div class="product-toolbar">
        <div>
          <p class="eyebrow">Curated Goods</p>
          <h2>暗夜精选</h2>
        </div>

        <div class="toolbar-controls">
          <el-radio-group v-model="sortMode" size="small">
            <el-radio-button value="推荐">推荐</el-radio-button>
            <el-radio-button value="销量">销量</el-radio-button>
            <el-radio-button value="价格">价格</el-radio-button>
          </el-radio-group>

          <el-checkbox v-model="inStockOnly">仅看有货</el-checkbox>

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

      <div v-if="displayedProducts.length" class="product-grid" :class="`product-grid--${viewMode}`">
        <article v-for="product in displayedProducts" :key="product.id" class="product-card">
          <div class="product-image-frame">
            <img
              v-if="!imageErrors.has(product.id)"
              :src="product.mainImage"
              :alt="product.name"
              loading="lazy"
              @error="markImageError(product.id)"
            />
            <span v-else>{{ product.name }}</span>
            <em>{{ productBadge(product) }}</em>
          </div>

          <div class="product-info">
            <div class="product-price">
              <strong>¥{{ product.price }}</strong>
              <span>{{ productRating(product) }} 分</span>
            </div>
            <RouterLink :to="`/products/${product.id}`">
              <h3>{{ product.name }}</h3>
            </RouterLink>
            <p>{{ product.subtitle }}</p>
            <div class="product-meta">
              <span>已售 {{ productSales(product) }}</span>
              <span :class="{ warning: product.stock <= 10 }">库存 {{ product.stock }}</span>
            </div>
            <button type="button" :disabled="product.stock <= 0" @click="addToCart(product)">加入购物车</button>
          </div>
        </article>
      </div>

      <div v-else class="empty-state">
        <p>没有找到匹配的商品。</p>
      </div>
    </section>

    <button class="ai-floating-button" type="button" @click="aiDialogVisible = true">
      <el-icon><MagicStick /></el-icon>
      AI 导购
    </button>

    <el-dialog
      v-model="aiDialogVisible"
      class="ai-guide-dialog"
      width="min(520px, calc(100vw - 32px))"
      title="夜幕 AI 导购"
      append-to-body
      destroy-on-close
    >
      <div class="ai-dialog-body">
        <p>告诉我你的预算、场景和偏好，我会从当前商品中给出搭配建议。</p>
        <el-input
          v-model="question"
          type="textarea"
          :rows="5"
          placeholder="例如：我想要一套适合晚宴的黑色配饰，预算 800 元"
        />
        <div class="ai-suggestion">
          <strong>示例建议</strong>
          <span>{{ aiPreview }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="aiDialogVisible = false">关闭</el-button>
        <el-button type="primary">
          <el-icon><MagicStick /></el-icon>
          生成建议
        </el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Search, ShoppingCart } from '@element-plus/icons-vue'
import { addCartItem } from '../api/cart'
import { getCategories, getProducts } from '../api/products'
import { useAuthStore } from '../stores/auth'
import type { Category, EntityId, Product } from '../types/product'

type ViewMode = 'compact' | 'comfortable' | 'large'
type SortMode = '推荐' | '销量' | '价格'

interface HeroSlide {
  kicker: string
  title: string
  description: string
  image: string
}

interface StoreProduct extends Product {
  badge?: string
  sales?: string
  salesCount?: number
  rating?: string
  priority?: number
}

const searchKeyword = ref('')
const authStore = useAuthStore()
const router = useRouter()
const activeCategoryId = ref<EntityId | null>(null)
const sortMode = ref<SortMode>('推荐')
const viewMode = ref<ViewMode>('comfortable')
const inStockOnly = ref(false)
const aiDialogVisible = ref(false)
const question = ref('')
const imageErrors = ref(new Set<EntityId>())

const categories = ref<Array<Pick<Category, 'id' | 'name'>>>([
  { id: 0, name: '全部' },
  { id: 2001, name: '服饰' },
  { id: 2002, name: '饰品' },
  { id: 2003, name: '香氛' },
  { id: 2004, name: '家居' }
])

const heroSlides: HeroSlide[] = [
  {
    kicker: 'Nocturne Atelier',
    title: '黑色仪式感，从日常开始',
    description: '斗篷、银饰与烛光器物组成克制而锋利的夜色衣橱。',
    image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1800&q=82'
  },
  {
    kicker: 'Silver Relics',
    title: '冷银配饰，贴近皮肤的暗光',
    description: '用低饱和金属、黑曜石和细链条完成一处安静的视觉重心。',
    image: 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?auto=format&fit=crop&w=1800&q=82'
  },
  {
    kicker: 'Candle & Scent',
    title: '乌木、焚香与长夜烛台',
    description: '为书桌、卧室和晚宴布置带来深色层次，不夸张但有存在感。',
    image: 'https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?auto=format&fit=crop&w=1800&q=82'
  }
]

const fallbackProducts: StoreProduct[] = [
  {
    id: 1,
    categoryId: 2001,
    categoryName: '服饰',
    name: '黑曜短斗篷外套',
    subtitle: '重磅斜纹面料，短款廓形，适合秋冬叠穿。',
    price: 899,
    mainImage: 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=82',
    badge: '主推',
    sales: '2800+',
    salesCount: 2800,
    stock: 18,
    rating: '4.9',
    priority: 98,
    detail: '黑色短斗篷外套，强调肩线和层次。',
    status: 1
  },
  {
    id: 2,
    categoryId: 2002,
    categoryName: '饰品',
    name: '冷银月相项链',
    subtitle: '925 银镀黑金，月相吊坠，可单戴或叠戴。',
    price: 369,
    mainImage: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&w=900&q=82',
    badge: '银饰',
    sales: '5100+',
    salesCount: 5100,
    stock: 42,
    rating: '4.8',
    priority: 96,
    detail: '低饱和银色项链，适合作为暗色衣装的视觉中心。',
    status: 1
  },
  {
    id: 3,
    categoryId: 2003,
    categoryName: '香氛',
    name: '乌木焚香香氛',
    subtitle: '乌木、没药与微弱烟草尾调，适合夜间空间。',
    price: 259,
    mainImage: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=82',
    badge: '低库存',
    sales: '1900+',
    salesCount: 1900,
    stock: 7,
    rating: '4.7',
    priority: 90,
    detail: '沉稳木质调香氛，适合卧室、书桌和安静的工作场景。',
    status: 1
  },
  {
    id: 4,
    categoryId: 2004,
    categoryName: '家居',
    name: '黄铜尖塔烛台',
    subtitle: '暗金拉丝质感，适合餐桌、书柜与玄关陈列。',
    price: 439,
    mainImage: 'https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?auto=format&fit=crop&w=900&q=82',
    badge: '暗金',
    sales: '960+',
    salesCount: 960,
    stock: 15,
    rating: '4.8',
    priority: 87,
    detail: '黄铜色尖塔烛台，提供复古、克制的空间装饰层次。',
    status: 1
  },
  {
    id: 5,
    categoryId: 2002,
    categoryName: '饰品',
    name: '黑曜石戒指套组',
    subtitle: '三枚组合，黑曜石、刻纹银圈和窄版素圈。',
    price: 299,
    mainImage: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=900&q=82',
    badge: '套组',
    sales: '3200+',
    salesCount: 3200,
    stock: 25,
    rating: '4.6',
    priority: 92,
    detail: '适合叠戴的戒指套组，覆盖日常和晚宴场景。',
    status: 1
  },
  {
    id: 6,
    categoryId: 2001,
    categoryName: '服饰',
    name: '暗纹丝绒手包',
    subtitle: '细密暗纹、磁扣开合，适合晚宴和日常通勤。',
    price: 529,
    mainImage: 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=82',
    badge: '新品',
    sales: '870+',
    salesCount: 870,
    stock: 11,
    rating: '4.7',
    priority: 89,
    detail: '丝绒触感手包，细节低调，容量适合日常随身物。',
    status: 1
  },
  {
    id: 7,
    categoryId: 2004,
    categoryName: '家居',
    name: '复古黑铁台灯',
    subtitle: '低照度暖光，黑铁灯身，适合书桌与床头。',
    price: 679,
    mainImage: 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=82',
    badge: '氛围',
    sales: '1400+',
    salesCount: 1400,
    stock: 9,
    rating: '4.8',
    priority: 91,
    detail: '黑铁材质台灯，适合营造稳定、安静的阅读光线。',
    status: 1
  },
  {
    id: 8,
    categoryId: 2003,
    categoryName: '香氛',
    name: '午夜玫瑰蜡烛',
    subtitle: '玫瑰、黑胡椒与树脂气息，燃烧时间约 42 小时。',
    price: 189,
    mainImage: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=82',
    badge: '香氛',
    sales: '4600+',
    salesCount: 4600,
    stock: 33,
    rating: '4.9',
    priority: 95,
    detail: '适合夜间空间的玫瑰调蜡烛，前调克制，尾调温暖。',
    status: 1
  }
]

const products = ref<StoreProduct[]>(fallbackProducts)

const displayedProducts = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  const result = products.value.filter((product) => {
    const matchCategory = activeCategoryId.value === null || product.categoryId === activeCategoryId.value
    const matchKeyword = !keyword || `${product.name}${product.subtitle}${product.categoryName}`.toLowerCase().includes(keyword)
    const matchStock = !inStockOnly.value || product.stock > 0
    return matchCategory && matchKeyword && matchStock
  })

  return [...result].sort((a, b) => {
    if (sortMode.value === '价格') return a.price - b.price
    if (sortMode.value === '销量') return (b.salesCount || 0) - (a.salesCount || 0)
    return (b.priority || Number(b.id) || 0) - (a.priority || Number(a.id) || 0)
  })
})

const aiPreview = computed(() => {
  if (question.value.trim()) {
    return '建议从冷银月相项链开始搭配，再加入午夜玫瑰蜡烛营造空间氛围。'
  }
  return '输入你的场景后，这里会显示一条可用于演示的导购建议。'
})

const roleLabel = computed(() => {
  const roles = authStore.user?.roles || []
  if (roles.includes('ADMIN')) return '系统管理员'
  if (roles.includes('OPERATOR')) return '运营管理员'
  if (roles.includes('USER')) return '普通用户'
  return '未分配角色'
})

function markImageError(productId: EntityId) {
  imageErrors.value = new Set([...imageErrors.value, productId])
}

function handleLogout() {
  authStore.clearSession()
}

function goCart() {
  router.push('/cart')
}

async function addToCart(product: StoreProduct) {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后加入购物车')
    router.push({ path: '/login', query: { redirect: '/' } })
    return
  }
  await addCartItem({ productId: product.id, quantity: 1 })
  ElMessage.success('已加入购物车')
}

function switchCategory(categoryId: EntityId) {
  activeCategoryId.value = categoryId === 0 ? null : categoryId
}

function productBadge(product: StoreProduct) {
  return product.badge || product.categoryName || '精选'
}

function productSales(product: StoreProduct) {
  return product.sales || `${Math.max(80, Number(product.id) % 9000 || 0)}+`
}

function productRating(product: StoreProduct) {
  return product.rating || '4.8'
}

async function loadHomeData() {
  try {
    const [categoryData, productPage] = await Promise.all([
      getCategories(),
      getProducts({ page: 1, size: 12 })
    ])
    categories.value = [{ id: 0, name: '全部' }, ...categoryData.map((category) => ({ id: category.id, name: category.name }))]
    products.value = productPage.records.map((product, index) => ({
      ...product,
      badge: product.categoryName,
      sales: `${900 + index * 420}+`,
      salesCount: 900 + index * 420,
      rating: '4.8',
      priority: 100 - index
    }))
  } catch {
    products.value = fallbackProducts
  }
}

onMounted(loadHomeData)
</script>
