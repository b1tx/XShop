import { http, type PageResult } from './http'
import type { Category, EntityId, Product } from '../types/product'

export interface ProductQuery {
  page?: number
  size?: number
  keyword?: string
  categoryId?: EntityId | null
}

export function getCategories() {
  return http.get<unknown, Category[]>('/categories')
}

export function getProducts(params: ProductQuery) {
  return http.get<unknown, PageResult<Product>>('/products', { params })
}

export function getProductDetail(id: EntityId) {
  return http.get<unknown, Product>(`/products/${id}`)
}
