import { chromium } from 'playwright'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, '../..')
const screenshotDir = path.join(repoRoot, 'docs', 'screenshots')
const baseUrl = process.env.SCREENSHOT_BASE_URL || 'http://127.0.0.1:5173'

async function main() {
  await mkdir(screenshotDir, { recursive: true })
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 })

  try {
    await ensureAppAvailable(page)

    await capture(page, '/login', 'login.png')
    await capture(page, '/register', 'register.png')
    await capture(page, '/', 'store-home-guest.png')

    await login(page, 'user', 'user123')
    await capture(page, '/', 'store-home-user.png')
    await captureSearchFilter(page)
    await capturePromotionExpanded(page)
    await captureAiGuideDialog(page)
    await capturePromotionCheckoutDialog(page)
    await capture(page, '/products/3001', 'product-detail.png')
    await captureProductQa(page)

    await capture(page, '/cart', 'cart.png')
    await captureCheckoutDialog(page)
    await capture(page, '/orders', 'orders.png')
    await captureOrderDetail(page)

    await login(page, 'admin', 'admin123')
    await capture(page, '/admin', 'admin-dashboard.png')
    await capture(page, '/admin/products', 'admin-products.png')
    await captureAdminProductDialog(page)
    await captureAdminCategoryDialog(page)
    await capture(page, '/admin/orders', 'admin-orders.png')
    await captureAdminOrderDrawer(page)
    await capture(page, '/admin/promotions', 'admin-promotions.png')
    await captureAdminPromotionDialog(page)
    await capture(page, '/admin/ai-operation', 'admin-ai-operation.png')
    await capture(page, '/admin/users', 'admin-users.png')
  } finally {
    await browser.close()
  }

  console.log(`Screenshots saved to ${screenshotDir}`)
}

async function ensureAppAvailable(page) {
  try {
    await page.goto(baseUrl, { waitUntil: 'networkidle', timeout: 15000 })
  } catch (error) {
    throw new Error(`Cannot open ${baseUrl}. Start backend :8080 and frontend :5173 before running screenshots. ${error.message}`)
  }
}

async function login(page, username, password) {
  await page.goto(`${baseUrl}/login`, { waitUntil: 'networkidle' })
  await page.locator('input').nth(0).fill(username)
  await page.locator('input').nth(1).fill(password)
  await page.getByRole('button', { name: /登录|登錄|鐧/ }).click()
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(500)
}

async function capture(page, route, filename) {
  await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(800)
  await page.screenshot({
    path: path.join(screenshotDir, filename),
    fullPage: true
  })
  console.log(`Captured ${filename}`)
}

async function captureCurrent(page, filename) {
  await page.waitForTimeout(800)
  await page.screenshot({
    path: path.join(screenshotDir, filename),
    fullPage: true
  })
  console.log(`Captured ${filename}`)
}

async function clickIfVisible(page, locator, timeout = 2500) {
  try {
    const target = locator.first()
    await target.waitFor({ state: 'visible', timeout })
    await target.click()
    await page.waitForLoadState('networkidle').catch(() => {})
    await page.waitForTimeout(500)
    return true
  } catch {
    return false
  }
}

async function fillIfVisible(page, locator, value, timeout = 2500) {
  try {
    const target = locator.first()
    await target.waitFor({ state: 'visible', timeout })
    await target.fill(value)
    await page.waitForTimeout(200)
    return true
  } catch {
    return false
  }
}

async function captureSearchFilter(page) {
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle' })
  await fillIfVisible(page, page.locator('.gothic-search input'), '银')
  await clickIfVisible(page, page.getByRole('button', { name: '饰品' }))
  await clickIfVisible(page, page.getByText('仅看有货'))
  await clickIfVisible(page, page.getByRole('radio', { name: '大图' }))
  await captureCurrent(page, 'store-search-filter.png')
}

async function capturePromotionExpanded(page) {
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle' })
  await clickIfVisible(page, page.getByRole('button', { name: /展开抢购|收起抢购/ }))
  await captureCurrent(page, 'promotion-expanded.png')
}

async function capturePromotionCheckoutDialog(page) {
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle' })
  await clickIfVisible(page, page.getByRole('button', { name: /展开抢购|收起抢购/ }))
  const opened = await clickIfVisible(page, page.getByRole('button', { name: '立即抢购' }))
  if (opened) {
    await fillIfVisible(page, page.locator('textarea').last(), '上海市浦东新区演示路 18 号')
  }
  await captureCurrent(page, 'promotion-checkout-dialog.png')
}

async function captureAiGuideDialog(page) {
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle' })
  const opened = await clickIfVisible(page, page.getByRole('button', { name: /AI 导购/ }))
  if (opened) {
    await fillIfVisible(page, page.locator('textarea').first(), '预算 800 元，想要一套适合晚宴的黑色配饰')
  }
  await captureCurrent(page, 'ai-guide-dialog.png')
}

async function captureProductQa(page) {
  await page.goto(`${baseUrl}/products/3001`, { waitUntil: 'networkidle' })
  await fillIfVisible(page, page.locator('textarea').first(), '这件商品适合什么场景？')
  await captureCurrent(page, 'product-qa.png')
}

async function captureCheckoutDialog(page) {
  await page.goto(`${baseUrl}/cart`, { waitUntil: 'networkidle' })
  const opened = await clickIfVisible(page, page.getByRole('button', { name: /结算|去结算|提交订单/ }))
  if (opened) {
    const inputs = page.locator('.el-dialog input')
    await fillIfVisible(page, inputs.nth(0), '演示用户')
    await fillIfVisible(page, inputs.nth(1), '13800000003')
    await fillIfVisible(page, page.locator('.el-dialog textarea').first(), '上海市浦东新区演示路 18 号')
  }
  await captureCurrent(page, 'checkout-dialog.png')
}

async function captureOrderDetail(page) {
  await page.goto(`${baseUrl}/orders`, { waitUntil: 'networkidle' })
  const detailClicked = await clickIfVisible(page, page.getByRole('button', { name: '详情' }))
  if (!detailClicked) {
    const linkClicked = await clickIfVisible(page, page.locator('a[href^="/orders/"]').first())
    if (!linkClicked) {
      await page.goto(`${baseUrl}/orders/1`, { waitUntil: 'networkidle' }).catch(() => {})
    }
  }
  await captureCurrent(page, 'order-detail.png')
}

async function captureAdminProductDialog(page) {
  await page.goto(`${baseUrl}/admin/products`, { waitUntil: 'networkidle' })
  await clickIfVisible(page, page.getByRole('button', { name: '新增商品' }))
  await captureCurrent(page, 'admin-product-dialog.png')
}

async function captureAdminCategoryDialog(page) {
  await page.goto(`${baseUrl}/admin/products`, { waitUntil: 'networkidle' })
  await clickIfVisible(page, page.getByRole('button', { name: '新增分类' }))
  await captureCurrent(page, 'admin-category-dialog.png')
}

async function captureAdminOrderDrawer(page) {
  await page.goto(`${baseUrl}/admin/orders`, { waitUntil: 'networkidle' })
  await clickIfVisible(page, page.getByRole('button', { name: '详情' }))
  await captureCurrent(page, 'admin-order-drawer.png')
}

async function captureAdminPromotionDialog(page) {
  await page.goto(`${baseUrl}/admin/promotions`, { waitUntil: 'networkidle' })
  await clickIfVisible(page, page.getByRole('button', { name: '新增活动' }))
  await captureCurrent(page, 'admin-promotion-dialog.png')
}

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
