import { http } from './http'
import type { UserProfile } from '../stores/auth'

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload extends LoginPayload {
  nickname: string
  phone?: string
}

export interface LoginResponse {
  token: string
  user: UserProfile
}

export function login(payload: LoginPayload) {
  return http.post<unknown, LoginResponse>('/auth/login', payload)
}

export function register(payload: RegisterPayload) {
  return http.post<unknown, LoginResponse>('/auth/register', payload)
}

export function getProfile() {
  return http.get<unknown, UserProfile>('/auth/profile')
}

