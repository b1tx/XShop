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
    await capture(page, '/', 'store-home.png')
    await capture(page, '/products/3001', 'product-detail.png')

    await login(page, 'user', 'user123')
    await capture(page, '/cart', 'cart.png')
    await capture(page, '/orders', 'orders.png')

    await login(page, 'admin', 'admin123')
    await capture(page, '/admin/products', 'admin-products.png')
    await capture(page, '/admin/orders', 'admin-orders.png')
    await capture(page, '/admin/promotions', 'admin-promotions.png')
    await capture(page, '/admin/ai-operation', 'admin-ai-operation.png')
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

main().catch((error) => {
  console.error(error.message)
  process.exit(1)
})
