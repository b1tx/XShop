export interface Category {
  id: number
  parentId: number
  name: string
  sort: number
  status: number
}

export interface Product {
  id: number
  categoryId: number
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
  categoryId: number
  name: string
  subtitle: string
  price: number
  stock: number
  mainImage: string
  detail: string
  status: number
}

