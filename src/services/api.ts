import type { AppUser, Store, Product, TryOnSession, AnalyticsSummary } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const TOKEN_KEY = 'tryonix:tokens:v1';

export interface Tokens {
  access_token: string;
  refresh_token: string;
}

export function getTokens(): Tokens | null {
  try {
    const raw = localStorage.getItem(TOKEN_KEY);
    return raw ? JSON.parse(raw) as Tokens : null;
  } catch {
    return null;
  }
}

export function saveTokens(tokens: Tokens): void {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function getAccessToken(): string | null {
  return getTokens()?.access_token ?? null;
}

class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const tokens = getTokens();
  if (!tokens?.refresh_token) return null;
  try {
    const resp = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokens.refresh_token }),
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    const updated = { ...tokens, access_token: data.access_token };
    saveTokens(updated);
    return data.access_token;
  } catch {
    return null;
  }
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) headers['Authorization'] = `Bearer ${token}`;

  if (options.body instanceof FormData) {
    // let browser set content-type for FormData
  } else if (options.body) {
    headers['Content-Type'] = 'application/json';
  }

  let resp = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (resp.status === 401 && token) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      resp = await fetch(`${API_BASE}${path}`, { ...options, headers });
    }
  }

  if (!resp.ok) {
    let detail = `Request failed (${resp.status})`;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch {
      // response has no JSON body
    }
    throw new ApiError(detail, resp.status);
  }

  return resp.json() as Promise<T>;
}

// ---- Auth ----

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AppUser;
}

export async function apiRegister(email: string, password: string, role: string, displayName: string): Promise<AuthResponse> {
  const data = await apiFetch<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, role, displayName }),
  });
  saveTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
  return data;
}

export async function apiLogin(email: string, password: string): Promise<AuthResponse> {
  const data = await apiFetch<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  saveTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
  return data;
}

export async function apiGetMe(): Promise<AppUser> {
  return apiFetch<AppUser>('/api/auth/me');
}

// ---- Stores ----

export async function apiGetStores(): Promise<Store[]> {
  return apiFetch<Store[]>('/api/stores');
}

export async function apiGetStoreBySlug(slug: string): Promise<Store> {
  return apiFetch<Store>(`/api/stores/${slug}`);
}

export async function apiCreateStore(data: {
  name: string;
  slug: string;
  tagline: string;
  description: string;
  logoText: string;
  bannerImage: string;
}): Promise<Store> {
  return apiFetch<Store>('/api/stores', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function apiUpdateStore(storeId: string, patch: {
  name?: string;
  tagline?: string;
  description?: string;
}): Promise<Store> {
  return apiFetch<Store>(`/api/stores/${storeId}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  });
}

// ---- Products ----

export async function apiGetProduct(productId: string): Promise<Product> {
  return apiFetch<Product>(`/api/products/${productId}`);
}

export async function apiGetStoreProducts(slug: string): Promise<Product[]> {
  return apiFetch<Product[]>(`/api/stores/${slug}/products`);
}

export async function apiCreateProduct(data: {
  storeId: string;
  name: string;
  description: string;
  category: string;
  price: string;
  variantsJson: string;
  image: File | null;
}): Promise<Product> {
  const fd = new FormData();
  fd.append('storeId', data.storeId);
  fd.append('name', data.name);
  fd.append('description', data.description);
  fd.append('category', data.category);
  fd.append('price', data.price);
  fd.append('variants_json', data.variantsJson);
  if (data.image) fd.append('image', data.image);
  return apiFetch<Product>('/api/products', { method: 'POST', body: fd });
}

export async function apiUpdateProduct(data: {
  productId: string;
  name?: string;
  description?: string;
  category?: string;
  price?: string;
  variantsJson?: string;
  image: File | null;
}): Promise<Product> {
  const fd = new FormData();
  if (data.name !== undefined) fd.append('name', data.name);
  if (data.description !== undefined) fd.append('description', data.description);
  if (data.category !== undefined) fd.append('category', data.category);
  if (data.price !== undefined) fd.append('price', data.price);
  if (data.variantsJson !== undefined) fd.append('variants_json', data.variantsJson);
  if (data.image) fd.append('image', data.image);
  return apiFetch<Product>(`/api/products/${data.productId}`, { method: 'PATCH', body: fd });
}

export async function apiDeleteProduct(productId: string): Promise<void> {
  await apiFetch<{ message: string }>(`/api/products/${productId}`, { method: 'DELETE' });
}

// ---- Try-On ----

export async function apiCreateTryOnSession(data: {
  productId: string;
  consent: boolean;
  personImage: File;
}): Promise<TryOnSession> {
  const fd = new FormData();
  fd.append('productId', data.productId);
  fd.append('consent', String(data.consent));
  fd.append('personImage', data.personImage);
  return apiFetch<TryOnSession>('/api/tryon/sessions', { method: 'POST', body: fd });
}

export async function apiGetTryOnSession(sessionId: string): Promise<TryOnSession> {
  return apiFetch<TryOnSession>(`/api/tryon/sessions/${sessionId}`);
}

// ---- Analytics ----

export async function apiGetAnalytics(storeId: string): Promise<AnalyticsSummary> {
  return apiFetch<AnalyticsSummary>(`/api/analytics/${storeId}`);
}

// ---- Admin ----

export async function apiGetAllUsers(): Promise<AppUser[]> {
  return apiFetch<AppUser[]>('/api/admin/users');
}

export async function apiToggleUserDisabled(userId: string): Promise<AppUser> {
  return apiFetch<AppUser>(`/api/admin/users/${userId}/toggle-disabled`, { method: 'PATCH' });
}

export async function apiGetAllSessions(): Promise<TryOnSession[]> {
  return apiFetch<TryOnSession[]>('/api/admin/sessions');
}

export async function apiGetFailedSessions(): Promise<TryOnSession[]> {
  return apiFetch<TryOnSession[]>('/api/admin/sessions/failed');
}

export { ApiError };
