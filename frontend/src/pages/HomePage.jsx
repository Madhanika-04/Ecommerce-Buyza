import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, TrendingUp, ShieldCheck, Truck, RefreshCw } from 'lucide-react';
import api from '../services/api';
import ProductCard from '../components/ProductCard';
import MLWorkflowCard from '../components/MLWorkflowCard';
import { useShop } from '../context/ShopContext';

export default function HomePage() {
  const { categories } = useShop();
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    setLoading(true);
    try {
      // 1. Fetch featured products
      const featRes = await api.getProducts({ page_size: 8, sort_by: 'reviews_desc' });
      setFeaturedProducts(featRes.data.items || []);

      // 2. Fetch ML recommendations for a popular flagship product (e.g., OnePlus Pad or Anker Soundcore)
      if (featRes.data.items && featRes.data.items.length > 0) {
        const sampleId = featRes.data.items[0].product_id;
        const recRes = await api.getRecommendations(sampleId, 4);
        setRecommendedProducts(recRes.data || []);
      }
    } catch (err) {
      console.error('Error loading home data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      
      {/* Hero Section */}
      <div className="relative rounded-3xl bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white overflow-hidden shadow-xl p-8 sm:p-12 mb-12 border border-slate-800">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 bg-blue-600/30 text-blue-300 text-xs font-semibold px-3 py-1.5 rounded-full border border-blue-500/30 mb-4 backdrop-blur-sm">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Smart Recommendations Engine • 76,000+ Verified Products</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
            India's Modern E-Commerce Catalog
          </h1>
          <p className="text-sm sm:text-base text-slate-300 mb-8 leading-relaxed">
            Discover electronics, fashion, cameras, and laptops priced in Indian Rupees (₹). Every product features live Content-Based Filtering powered by TF-IDF vectorization and sub-5ms Cosine Similarity.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              to="/products"
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm px-6 py-3 rounded-xl shadow-lg shadow-blue-600/30 flex items-center space-x-2 transition active:scale-95"
            >
              <span>Explore Full Catalog</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/products?category=Laptops%20%26%20Computers"
              className="bg-slate-800/80 hover:bg-slate-700 text-slate-200 font-semibold text-sm px-6 py-3 rounded-xl border border-slate-700 transition"
            >
              View Laptops & Tech
            </Link>
          </div>
        </div>

        {/* Decorative Indian Rupee Accent */}
        <div className="absolute right-6 -bottom-10 opacity-10 font-bold text-[280px] pointer-events-none select-none text-white font-sans">
          ₹
        </div>
      </div>

      {/* Category Pills Slider */}
      <div className="mb-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900">Explore Departments</h2>
          <Link to="/products" className="text-sm font-semibold text-blue-600 hover:text-blue-800 flex items-center">
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-3">
          {categories.map((cat) => (
            <Link
              key={cat.category}
              to={`/products?category=${encodeURIComponent(cat.category)}`}
              className="bg-white hover:bg-blue-50/70 border border-slate-200/90 rounded-xl p-3 text-center transition shadow-sm hover:border-blue-300 flex flex-col items-center justify-center group"
            >
              <span className="text-xs font-semibold text-slate-800 group-hover:text-blue-600 line-clamp-1">
                {cat.category}
              </span>
              <span className="text-[10px] text-slate-400 mt-1">
                {cat.product_count?.toLocaleString()} items
              </span>
            </Link>
          ))}
        </div>
      </div>

      {/* Featured Products Grid */}
      <div className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-bold text-slate-900">Most Popular Across India</h2>
          </div>
          <span className="text-xs text-slate-500 font-medium">Ranked by real customer review volume</span>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-64 bg-slate-200/70 rounded-xl animate-pulse"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </div>
        )}
      </div>

      {/* Machine Learning Architecture Card */}
      <MLWorkflowCard />

      {/* Recommended For You Section */}
      {recommendedProducts.length > 0 && (
        <div className="mb-12">
          <div className="flex items-center space-x-2 mb-6">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <h2 className="text-xl font-bold text-slate-900">AI Recommendations Showcase</h2>
            <span className="text-xs bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full font-bold ml-2">
              Live TF-IDF Matching
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {recommendedProducts.map((product) => (
              <ProductCard key={product.product_id} product={product} showSimilarity={true} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
