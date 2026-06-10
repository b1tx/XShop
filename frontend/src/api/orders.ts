import { http, type PageResult } from './http'
import type { CreateOrderPayload, Order } from '../types/order'
import type { EntityId } from '../types/product'

export interface OrderQuery {
  page?: number
  size?: number
  status?: string | null
}

export function createOrder(payload: CreateOrderPayload) {
  return http.post<unknown, Order>('/orders', payload)
}

export function getOrders(params: OrderQuery) {
  return http.get<unknown, PageResult<Order>>('/orders', { params })
}

export function getOrderDetail(id: EntityId) {
  return http.get<unknown, Order>(`/orders/${id}`)
}

export function payOrder(id: EntityId) {
  return http.post<unknown, Order>(`/orders/${id}/pay`)
}

export function cancelOrder(id: EntityId) {
  return http.post<unknown, Order>(`/orders/${id}/cancel`)
}

export function receiveOrder(id: EntityId) {
  return http.post<unknown, Order>(`/orders/${id}/receive`)
}
