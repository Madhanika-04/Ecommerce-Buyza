import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingBag, Heart, Package, Sparkles, MapPin } from 'lucide-react';
import { useShop } from '../context/ShopContext';

export default function Navbar() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const { cart, wishlist, categories } = useShop();
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchTerm.trim() && !selectedCategory) return;
    const queryParams = new URLSearchParams();
    if (searchTerm.trim()) queryParams.set('search', searchTerm.trim());
    if (selectedCategory) queryParams.set('category', selectedCategory);
    navigate(`/products?${queryParams.toString()}`);
  };

  return (
    <header className="sticky top-0 z-40 bg-slate-900 text-white shadow-md">
      {/* Top micro-bar: Indian localization & AI recommendation banner */}
      <div className="bg-slate-950 px-4 py-1.5 text-xs text-slate-300 flex justify-between items-center border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Pan-India Delivery across 19,000+ PIN Codes</span>
          <span className="text-slate-500">|</span>
          <span className="flex items-center text-amber-400 font-medium">
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            AI Content-Based Recommendations Online
          </span>
        </div>
        <div className="hidden sm:flex items-center space-x-4 text-slate-400">
          <span className="flex items-center"><MapPin className="w-3 h-3 mr-1 text-slate-400" /> Deliver to: India</span>
          <span>₹ INR Formatting</span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 space-x-4">
          
          {/* Brand Logo & Name */}
          <Link to="/" className="flex items-center space-x-2 flex-shrink-0 group">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-md group-hover:bg-blue-500 transition">
              ₹
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-base tracking-tight text-white group-hover:text-blue-400 transition font-sans">
                E-Commerce
              </span>
              <span className="text-[10px] tracking-wider uppercase text-blue-400 font-semibold -mt-1">
                Recommendation System
              </span>
            </div>
          </Link>

          {/* Search Bar with Category Select */}
          <form onSubmit={handleSearch} className="flex-1 max-w-2xl mx-4 hidden md:flex">
            <div className="relative flex w-full">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-slate-800 text-slate-200 text-xs font-medium rounded-l-lg px-3 border border-r-0 border-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500 max-w-[150px] truncate"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat.category} value={cat.category}>
                    {cat.category}
                  </option>
                ))}
              </select>

              <input
                type="text"
                placeholder="Search 76,000+ products (e.g. laptop, running shoes, wireless)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-800 text-white placeholder-slate-400 text-sm px-4 py-2 border-y border-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />

              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-500 text-white px-5 rounded-r-lg font-medium text-sm flex items-center justify-center transition border border-l-0 border-blue-600"
              >
                <Search className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Right Action Icons: Catalog, Wishlist, Cart, Orders */}
          <div className="flex items-center space-x-5 flex-shrink-0">
            <Link
              to="/products"
              className="text-slate-300 hover:text-white text-sm font-medium transition hidden lg:inline-block"
            >
              All Products
            </Link>

            {/* Wishlist Link */}
            <Link
              to="/wishlist"
              className="relative p-2 text-slate-300 hover:text-white transition flex items-center"
              title="Saved Wishlist"
            >
              <Heart className="w-5 h-5" />
              {wishlist.total_items > 0 && (
                <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-[10px] font-bold rounded-full h-4 w-4 flex items-center justify-center">
                  {wishlist.total_items}
                </span>
              )}
            </Link>

            {/* Cart Link */}
            <Link
              to="/cart"
              className="relative p-2 text-slate-300 hover:text-white transition flex items-center"
              title="Shopping Cart"
            >
              <ShoppingBag className="w-5 h-5" />
              {cart.total_items > 0 && (
                <span className="absolute -top-1 -right-1 bg-amber-500 text-slate-950 text-[10px] font-extrabold rounded-full h-4 w-4 flex items-center justify-center">
                  {cart.total_items}
                </span>
              )}
            </Link>

            {/* Orders Link */}
            <Link
              to="/orders"
              className="p-2 text-slate-300 hover:text-white transition flex items-center space-x-1"
              title="My Orders"
            >
              <Package className="w-5 h-5" />
              <span className="text-xs font-medium hidden sm:inline">Orders</span>
            </Link>
          </div>
        </div>

        {/* Mobile Search Bar */}
        <div className="md:hidden pb-3">
          <form onSubmit={handleSearch} className="flex">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-800 text-white placeholder-slate-400 text-sm px-3 py-2 rounded-l-md border border-r-0 border-slate-700 focus:outline-none"
            />
            <button
              type="submit"
              className="bg-blue-600 px-4 rounded-r-md text-white flex items-center justify-center"
            >
              <Search className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </header>
  );
}
