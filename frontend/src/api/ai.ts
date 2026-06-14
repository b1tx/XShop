import { http } from './http'
import type { AiResponse, ProductCopywritingPayload } from '../types/ai'
import type { EntityId } from '../types/product'

export function shoppingGuide(message: string) {
  return http.post<unknown, AiResponse>('/ai/shopping-guide', { message })
}

export function productQa(productId: EntityId, question: string) {
  return http.post<unknown, AiResponse>('/ai/product-qa', { productId, question })
}

export function productCopywriting(payload: ProductCopywritingPayload) {
  return http.post<unknown, AiResponse>('/ai/product-copywriting', payload)
}

export function operationAnalysis(dateRange: string, focus: string) {
  return http.post<unknown, AiResponse>('/ai/operation-analysis', { dateRange, focus })
}
