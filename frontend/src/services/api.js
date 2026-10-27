import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const api = {
  // System Health
  getHealth: () => apiClient.get('/health'),

  // Categories
  getCategories: () => apiClient.get('/categories'),

  // Products
  getProducts: (params = {}) => apiClient.get('/products', { params }),
  getProductById: (productId) => apiClient.get(`/products/${productId}`),
  
  // Recommendations & Semantic Search
  getRecommendations: (productId, topN = 6, category = null) => {
    const params = { top_n: topN };
    if (category) params.category = category;
    return apiClient.get(`/products/${productId}/recommendations`, { params });
  },
  
  searchProducts: (query, topN = 12, category = null) => {
    const params = { q: query, top_n: topN };
    if (category) params.category = category;
    return apiClient.get('/search', { params });
  },

  // Cart
  getCart: (userId = 'guest_user') => apiClient.get('/cart', { params: { user_id: userId } }),
  addToCart: (productId, quantity = 1, userId = 'guest_user') =>
    apiClient.post('/cart', { product_id: productId, quantity, user_id: userId }),
  updateCartQuantity: (productId, quantity, userId = 'guest_user') =>
    apiClient.patch(`/cart/${productId}`, { quantity, user_id: userId }),
  removeFromCart: (productId, userId = 'guest_user') =>
    apiClient.delete(`/cart/${productId}`, { params: { user_id: userId } }),
  clearCart: (userId = 'guest_user') =>
    apiClient.delete('/cart', { params: { user_id: userId } }),

  // Wishlist
  getWishlist: (userId = 'guest_user') => apiClient.get('/wishlist', { params: { user_id: userId } }),
  addToWishlist: (productId, userId = 'guest_user') =>
    apiClient.post('/wishlist', { product_id: productId, user_id: userId }),
  removeFromWishlist: (productId, userId = 'guest_user') =>
    apiClient.delete(`/wishlist/${productId}`, { params: { user_id: userId } }),

  // Orders
  placeOrder: (orderData) => apiClient.post('/orders', orderData),
  getOrders: (userId = 'guest_user') => apiClient.get('/orders', { params: { user_id: userId } }),
  getOrderById: (orderId, userId = 'guest_user') =>
    apiClient.get(`/orders/${orderId}`, { params: { user_id: userId } }),
};

export default api;
