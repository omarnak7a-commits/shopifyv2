import type { Store, Product, AnalyticsSummary, AppUser, TryOnSession } from '../types';
import {
  apiGetStores,
  apiGetStoreBySlug,
  apiCreateStore,
  apiUpdateStore,
  apiGetProduct,
  apiGetStoreProducts,
  apiCreateProduct,
  apiUpdateProduct,
  apiDeleteProduct,
  apiGetAnalytics,
  apiGetAllUsers,
  apiToggleUserDisabled,
  apiGetAllSessions,
  apiGetFailedSessions,
} from './api';

// ---- Stores ----

export async function getStores(): Promise<Store[]> {
  return apiGetStores();
}

export async function getStoreBySlug(slug: string): Promise<Store | null> {
  try {
    return await apiGetStoreBySlug(slug);
  } catch {
    return null;
  }
}

export async function getStoresByOwner(_ownerId: string): Promise<Store[]> {
  const all = await apiGetStores();
  return all;
}

export async function createStore(data: {
  name: string;
  slug: string;
  tagline: string;
  description: string;
  logoText: string;
  bannerImage: string;
}): Promise<Store> {
  return apiCreateStore(data);
}

export async function updateStore(storeId: string, patch: {
  name?: string;
  tagline?: string;
  description?: string;
}): Promise<Store> {
  return apiUpdateStore(storeId, patch);
}

// ---- Products ----

export async function getProducts(): Promise<Product[]> {
  const stores = await apiGetStores();
  const all: Product[] = [];
  for (const s of stores) {
    const prods = await apiGetStoreProducts(s.slug);
    all.push(...prods);
  }
  return all;
}

export async function getProductsByStore(slug: string): Promise<Product[]> {
  return apiGetStoreProducts(slug);
}

export async function getProductsByStoreId(storeId: string): Promise<Product[]> {
  const stores = await apiGetStores();
  const store = stores.find((s) => s.id === storeId);
  if (!store) return [];
  return apiGetStoreProducts(store.slug);
}

export async function getProductById(id: string): Promise<Product | null> {
  try {
    return await apiGetProduct(id);
  } catch {
    return null;
  }
}

export async function createProduct(data: {
  storeId: string;
  name: string;
  description: string;
  category: string;
  price: number | null;
  image: File | null;
  variants: { color: string; colorHex: string; sizes: string[] }[];
}): Promise<Product> {
  return apiCreateProduct({
    storeId: data.storeId,
    name: data.name,
    description: data.description,
    category: data.category,
    price: data.price?.toString() ?? '',
    variantsJson: JSON.stringify(data.variants),
    image: data.image,
  });
}

export async function updateProduct(productId: string, data: {
  name?: string;
  description?: string;
  category?: string;
  price?: number | null;
  image?: File | null;
  variants?: { color: string; colorHex: string; sizes: string[] }[];
}): Promise<Product> {
  return apiUpdateProduct({
    productId,
    name: data.name,
    description: data.description,
    category: data.category,
    price: data.price?.toString() ?? '',
    variantsJson: data.variants ? JSON.stringify(data.variants) : undefined,
    image: data.image ?? null,
  });
}

export async function deleteProduct(id: string): Promise<boolean> {
  try {
    await apiDeleteProduct(id);
    return true;
  } catch {
    return false;
  }
}

// ---- Analytics ----

export async function getAnalyticsForStore(storeId: string): Promise<AnalyticsSummary> {
  return apiGetAnalytics(storeId);
}

// ---- Users (admin) ----

export async function getAllUsers(): Promise<AppUser[]> {
  return apiGetAllUsers();
}

export async function toggleUserDisabled(id: string): Promise<AppUser | null> {
  try {
    return await apiToggleUserDisabled(id);
  } catch {
    return null;
  }
}

export async function getAllSessions(): Promise<TryOnSession[]> {
  return apiGetAllSessions();
}

export async function getFailedSessions(): Promise<TryOnSession[]> {
  return apiGetFailedSessions();
}
