import { http } from './http'
import type { CartItem, CartItemPayload } from '../types/cart'
import type { EntityId } from '../types/product'

export function getCartItems() {
  return http.get<unknown, CartItem[]>('/cart/items')
}

export function addCartItem(payload: CartItemPayload) {
  return http.post<unknown, CartItem>('/cart/items', payload)
}

export function updateCartItemQuantity(id: EntityId, quantity: number) {
  return http.put<unknown, CartItem>(`/cart/items/${id}`, { quantity })
}

export function deleteCartItem(id: EntityId) {
  return http.delete<unknown, void>(`/cart/items/${id}`)
}
