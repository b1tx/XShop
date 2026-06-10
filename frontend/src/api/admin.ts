import { http, type PageResult } from './http'
import type { Category, EntityId, Product, ProductPayload } from '../types/product'
import type { UserProfile } from '../stores/auth'
import type { Order } from '../types/order'

export interface AdminProductQuery {
  page?: number
  size?: number
  keyword?: string
  categoryId?: EntityId | null
  status?: number | null
}

export interface AdminUserQuery {
  page?: number
  size?: number
  keyword?: string
}

export interface AdminOrderQuery {
  page?: number
  size?: number
  keyword?: string
  status?: string | null
}

export function getAdminCategories() {
  return http.get<unknown, Category[]>('/admin/categories')
}

export function createAdminCategory(payload: Pick<Category, 'name' | 'sort' | 'status'>) {
  return http.post<unknown, Category>('/admin/categories', payload)
}

export function getAdminProducts(params: AdminProductQuery) {
  return http.get<unknown, PageResult<Product>>('/admin/products', { params })
}

export function createAdminProduct(payload: ProductPayload) {
  return http.post<unknown, Product>('/admin/products', payload)
}

export function updateAdminProduct(id: EntityId, payload: ProductPayload) {
  return http.put<unknown, Product>(`/admin/products/${id}`, payload)
}

export function updateAdminProductStatus(id: EntityId, status: number) {
  return http.put<unknown, void>(`/admin/products/${id}/status`, { status })
}

export function deleteAdminProduct(id: EntityId) {
  return http.delete<unknown, void>(`/admin/products/${id}`)
}

export interface AdminUser extends UserProfile {
  createdAt: string
}

export function getAdminUsers(params: AdminUserQuery) {
  return http.get<unknown, PageResult<AdminUser>>('/admin/users', { params })
}

export function updateAdminUserStatus(id: EntityId, status: number) {
  return http.put<unknown, void>(`/admin/users/${id}/status`, { status })
}

export function updateAdminUserRoles(id: EntityId, roles: string[]) {
  return http.put<unknown, void>(`/admin/users/${id}/roles`, { roles })
}

export function getAdminOrders(params: AdminOrderQuery) {
  return http.get<unknown, PageResult<Order>>('/admin/orders', { params })
}

export function getAdminOrderDetail(id: EntityId) {
  return http.get<unknown, Order>(`/admin/orders/${id}`)
}

export function shipAdminOrder(id: EntityId) {
  return http.put<unknown, Order>(`/admin/orders/${id}/ship`)
}

export function cancelAdminOrder(id: EntityId) {
  return http.put<unknown, Order>(`/admin/orders/${id}/cancel`)
}
