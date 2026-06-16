import { http } from './http'

export interface UploadResponse {
  url: string
  objectKey: string
}

export function uploadProductImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return http.post<unknown, UploadResponse>('/admin/uploads/product-images', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000
  })
}
