import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const ShopContext = createContext();

export const ShopProvider = ({ children }) => {
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState({ items: [], total_items: 0, total_inr: 0, formatted_total: '₹0' });
  const [wishlist, setWishlist] = useState({ items: [], total_items: 0 });
  const [loading, setLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (message) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Initial load: Categories, Cart, and Wishlist
  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const [catRes, cartRes, wishRes] = await Promise.allSettled([
        api.getCategories(),
        api.getCart(),
        api.getWishlist(),
      ]);

      if (catRes.status === 'fulfilled') setCategories(catRes.value.data);
      if (cartRes.status === 'fulfilled') setCart(cartRes.value.data);
      if (wishRes.status === 'fulfilled') setWishlist(wishRes.value.data);
    } catch (err) {
      console.error('Failed to load initial data:', err);
    }
  };

  // Cart Handlers
  const addToCart = async (productId, quantity = 1) => {
    try {
      const res = await api.addToCart(productId, quantity);
      setCart(res.data);
      showToast('Item added to cart!');
    } catch (err) {
      console.error('Error adding to cart:', err);
      showToast('Failed to add item to cart');
    }
  };

  const updateCartQuantity = async (productId, quantity) => {
    try {
      const res = await api.updateCartQuantity(productId, quantity);
      setCart(res.data);
    } catch (err) {
      console.error('Error updating quantity:', err);
    }
  };

  const removeFromCart = async (productId) => {
    try {
      const res = await api.removeFromCart(productId);
      setCart(res.data);
      showToast('Item removed from cart');
    } catch (err) {
      console.error('Error removing from cart:', err);
    }
  };

  // Wishlist Handlers
  const addToWishlist = async (productId) => {
    try {
      const res = await api.addToWishlist(productId);
      setWishlist(res.data);
      showToast('Added to wishlist!');
    } catch (err) {
      console.error('Error adding to wishlist:', err);
    }
  };

  const removeFromWishlist = async (productId) => {
    try {
      const res = await api.removeFromWishlist(productId);
      setWishlist(res.data);
      showToast('Removed from wishlist');
    } catch (err) {
      console.error('Error removing from wishlist:', err);
    }
  };

  const isInWishlist = (productId) => {
    return wishlist.items.some((item) => item.product_id === productId);
  };

  const clearCartState = () => {
    setCart({ items: [], total_items: 0, total_inr: 0, formatted_total: '₹0' });
  };

  return (
    <ShopContext.Provider
      value={{
        categories,
        cart,
        wishlist,
        loading,
        addToCart,
        updateCartQuantity,
        removeFromCart,
        addToWishlist,
        removeFromWishlist,
        isInWishlist,
        clearCartState,
        refreshCart: () => api.getCart().then((res) => setCart(res.data)),
        refreshWishlist: () => api.getWishlist().then((res) => setWishlist(res.data)),
        showToast,
      }}
    >
      {children}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-navy-900 text-white px-5 py-3 rounded-lg shadow-xl border border-slate-700 flex items-center space-x-2 animate-bounce">
          <span className="text-emerald-400 font-bold">✓</span>
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}
    </ShopContext.Provider>
  );
};

export const useShop = () => useContext(ShopContext);
