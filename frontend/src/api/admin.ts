import { http, type PageResult } from './http'
import type { Category, Product, ProductPayload } from '../types/product'
import type { UserProfile } from '../stores/auth'

export interface AdminProductQuery {
  page?: number
  size?: number
  keyword?: string
  categoryId?: number | null
  status?: number | null
}

export interface AdminUserQuery {
  page?: number
  size?: number
  keyword?: string
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

export function updateAdminProduct(id: number, payload: ProductPayload) {
  return http.put<unknown, Product>(`/admin/products/${id}`, payload)
}

export function updateAdminProductStatus(id: number, status: number) {
  return http.put<unknown, void>(`/admin/products/${id}/status`, { status })
}

export function deleteAdminProduct(id: number) {
  return http.delete<unknown, void>(`/admin/products/${id}`)
}

export interface AdminUser extends UserProfile {
  createdAt: string
}

export function getAdminUsers(params: AdminUserQuery) {
  return http.get<unknown, PageResult<AdminUser>>('/admin/users', { params })
}

export function updateAdminUserStatus(id: number, status: number) {
  return http.put<unknown, void>(`/admin/users/${id}/status`, { status })
}

export function updateAdminUserRoles(id: number, roles: string[]) {
  return http.put<unknown, void>(`/admin/users/${id}/roles`, { roles })
}

