<template>
  <main class="store-shell gothic-store">
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
            :key="category"
            :class="{ active: activeCategory === category }"
            type="button"
            @click="activeCategory = category"
          >
            {{ category }}
          </button>
        </nav>

        <div class="gothic-actions">
          <RouterLink to="/admin">后台</RouterLink>
          <button type="button">
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
              :src="product.image"
              :alt="product.name"
              loading="lazy"
              @error="markImageError(product.id)"
            />
            <span v-else>{{ product.name }}</span>
            <em>{{ product.badge }}</em>
          </div>

          <div class="product-info">
            <div class="product-price">
              <strong>¥{{ product.price }}</strong>
              <span>{{ product.rating }} 分</span>
            </div>
            <h3>{{ product.name }}</h3>
            <p>{{ product.subtitle }}</p>
            <div class="product-meta">
              <span>已售 {{ product.sales }}</span>
              <span :class="{ warning: product.stock <= 10 }">库存 {{ product.stock }}</span>
            </div>
            <button type="button">加入购物车</button>
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
import { computed, ref } from 'vue'
import { MagicStick, Search, ShoppingCart } from '@element-plus/icons-vue'

type ViewMode = 'compact' | 'comfortable' | 'large'
type SortMode = '推荐' | '销量' | '价格'

interface HeroSlide {
  kicker: string
  title: string
  description: string
  image: string
}

interface Product {
  id: number
  category: string
  name: string
  subtitle: string
  price: number
  image: string
  badge: string
  sales: string
  salesCount: number
  stock: number
  rating: string
  priority: number
}

const searchKeyword = ref('')
const activeCategory = ref('全部')
const sortMode = ref<SortMode>('推荐')
const viewMode = ref<ViewMode>('comfortable')
const inStockOnly = ref(false)
const aiDialogVisible = ref(false)
const question = ref('')
const imageErrors = ref(new Set<number>())

const categories = ['全部', '服饰', '饰品', '香氛', '家居']

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

const products: Product[] = [
  {
    id: 1,
    category: '服饰',
    name: '黑曜短斗篷外套',
    subtitle: '重磅斜纹面料，短款廓形，适合秋冬叠穿。',
    price: 899,
    image: 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=82',
    badge: '主推',
    sales: '2800+',
    salesCount: 2800,
    stock: 18,
    rating: '4.9',
    priority: 98
  },
  {
    id: 2,
    category: '饰品',
    name: '冷银月相项链',
    subtitle: '925 银镀黑金，月相吊坠，可单戴或叠戴。',
    price: 369,
    image: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&w=900&q=82',
    badge: '银饰',
    sales: '5100+',
    salesCount: 5100,
    stock: 42,
    rating: '4.8',
    priority: 96
  },
  {
    id: 3,
    category: '香氛',
    name: '乌木焚香香氛',
    subtitle: '乌木、没药与微弱烟草尾调，适合夜间空间。',
    price: 259,
    image: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=82',
    badge: '低库存',
    sales: '1900+',
    salesCount: 1900,
    stock: 7,
    rating: '4.7',
    priority: 90
  },
  {
    id: 4,
    category: '家居',
    name: '黄铜尖塔烛台',
    subtitle: '暗金拉丝质感，适合餐桌、书柜与玄关陈列。',
    price: 439,
    image: 'https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?auto=format&fit=crop&w=900&q=82',
    badge: '暗金',
    sales: '960+',
    salesCount: 960,
    stock: 15,
    rating: '4.8',
    priority: 87
  },
  {
    id: 5,
    category: '饰品',
    name: '黑曜石戒指套组',
    subtitle: '三枚组合，黑曜石、刻纹银圈和窄版素圈。',
    price: 299,
    image: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=900&q=82',
    badge: '套组',
    sales: '3200+',
    salesCount: 3200,
    stock: 25,
    rating: '4.6',
    priority: 92
  },
  {
    id: 6,
    category: '服饰',
    name: '暗纹丝绒手包',
    subtitle: '细密暗纹、磁扣开合，适合晚宴和日常通勤。',
    price: 529,
    image: 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=82',
    badge: '新品',
    sales: '870+',
    salesCount: 870,
    stock: 11,
    rating: '4.7',
    priority: 89
  },
  {
    id: 7,
    category: '家居',
    name: '复古黑铁台灯',
    subtitle: '低照度暖光，黑铁灯身，适合书桌与床头。',
    price: 679,
    image: 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=82',
    badge: '氛围',
    sales: '1400+',
    salesCount: 1400,
    stock: 9,
    rating: '4.8',
    priority: 91
  },
  {
    id: 8,
    category: '香氛',
    name: '午夜玫瑰蜡烛',
    subtitle: '玫瑰、黑胡椒与树脂气息，燃烧时间约 42 小时。',
    price: 189,
    image: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=82',
    badge: '香氛',
    sales: '4600+',
    salesCount: 4600,
    stock: 33,
    rating: '4.9',
    priority: 95
  }
]

const displayedProducts = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  const result = products.filter((product) => {
    const matchCategory = activeCategory.value === '全部' || product.category === activeCategory.value
    const matchKeyword = !keyword || `${product.name}${product.subtitle}${product.category}`.toLowerCase().includes(keyword)
    const matchStock = !inStockOnly.value || product.stock > 0
    return matchCategory && matchKeyword && matchStock
  })

  return [...result].sort((a, b) => {
    if (sortMode.value === '价格') return a.price - b.price
    if (sortMode.value === '销量') return b.salesCount - a.salesCount
    return b.priority - a.priority
  })
})

const aiPreview = computed(() => {
  if (question.value.trim()) {
    return '建议从冷银月相项链开始搭配，再加入午夜玫瑰蜡烛营造空间氛围。'
  }
  return '输入你的场景后，这里会显示一条可用于演示的导购建议。'
})

function markImageError(productId: number) {
  imageErrors.value = new Set([...imageErrors.value, productId])
}
</script>
