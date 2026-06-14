import { http, type PageResult } from './http'
import type { Order } from '../types/order'
import type { EntityId } from '../types/product'
import type { Promotion, PromotionOrderPayload, PromotionPayload } from '../types/promotion'

export interface AdminPromotionQuery {
  page?: number
  size?: number
  keyword?: string
  status?: number | null
}

export function getActivePromotions() {
  return http.get<unknown, Promotion[]>('/promotions/active')
}

export function getPromotionDetail(id: EntityId) {
  return http.get<unknown, Promotion>(`/promotions/${id}`)
}

export function createPromotionOrder(id: EntityId, payload: PromotionOrderPayload) {
  return http.post<unknown, Order>(`/promotions/${id}/orders`, payload)
}

export function getAdminPromotions(params: AdminPromotionQuery) {
  return http.get<unknown, PageResult<Promotion>>('/admin/promotions', { params })
}

export function getAdminPromotionDetail(id: EntityId) {
  return http.get<unknown, Promotion>(`/admin/promotions/${id}`)
}

export function createAdminPromotion(payload: PromotionPayload) {
  return http.post<unknown, Promotion>('/admin/promotions', payload)
}

export function updateAdminPromotion(id: EntityId, payload: PromotionPayload) {
  return http.put<unknown, Promotion>(`/admin/promotions/${id}`, payload)
}

export function updateAdminPromotionStatus(id: EntityId, status: number) {
  return http.put<unknown, void>(`/admin/promotions/${id}/status`, { status })
}
