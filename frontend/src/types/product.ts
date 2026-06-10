export type EntityId = string | number

export interface Category {
  id: EntityId
  parentId: EntityId
  name: string
  sort: number
  status: number
}

export interface Product {
  id: EntityId
  categoryId: EntityId
  categoryName: string
  name: string
  subtitle: string
  price: number
  stock: number
  mainImage: string
  detail: string
  status: number
  createdAt?: string
  updatedAt?: string
}

export interface ProductPayload {
  categoryId: EntityId
  name: string
  subtitle: string
  price: number
  stock: number
  mainImage: string
  detail: string
  status: number
}
