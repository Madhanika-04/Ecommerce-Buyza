import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, ShoppingBag, Star, Sparkles } from 'lucide-react';
import { useShop } from '../context/ShopContext';

// Color map for distinct category badges
const CATEGORY_COLORS = {
  "Laptops & Computers": "bg-indigo-50 text-indigo-700 border-indigo-200",
  "Mobiles & Tablets": "bg-blue-50 text-blue-700 border-blue-200",
  "Cameras & Photography": "bg-emerald-50 text-emerald-700 border-emerald-200",
  "Audio & Video": "bg-purple-50 text-purple-700 border-purple-200",
  "Men's Fashion": "bg-rose-50 text-rose-700 border-rose-200",
  "Men's Footwear": "bg-amber-50 text-amber-700 border-amber-200",
  "Automotive & Car Accessories": "bg-cyan-50 text-cyan-700 border-cyan-200",
  "Movies & Entertainment": "bg-violet-50 text-violet-700 border-violet-200",
  "Toys & Games": "bg-orange-50 text-orange-700 border-orange-200",
};

export default function ProductCard({ product, showSimilarity = false }) {
  const { addToCart, addToWishlist, removeFromWishlist, isInWishlist } = useShop();
  const isWishlisted = isInWishlist(product.product_id);

  const badgeClass = CATEGORY_COLORS[product.category] || "bg-slate-100 text-slate-700 border-slate-200";

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between overflow-hidden group">
      <div className="p-4 flex-1 flex flex-col">
        {/* Top Meta: Category Badge & Similarity Score / Wishlist */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badgeClass} truncate max-w-[170px]`}>
            {product.category}
          </span>
          <button
            onClick={() => isWishlisted ? removeFromWishlist(product.product_id) : addToWishlist(product.product_id)}
            className="text-slate-400 hover:text-rose-500 transition p-1"
            title={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
          >
            <Heart className={`w-4 h-4 ${isWishlisted ? "fill-rose-500 text-rose-500" : ""}`} />
          </button>
        </div>

        {/* Similarity Score Pill (if present from ML recommendation) */}
        {showSimilarity && product.similarity_score !== undefined && (
          <div className="mb-2">
            <span className="inline-flex items-center text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-300">
              <Sparkles className="w-3 h-3 mr-1 text-emerald-600" />
              {(product.similarity_score * 100).toFixed(1)}% Match
            </span>
          </div>
        )}

        {/* Product Title */}
        <Link
          to={`/products/${product.product_id}`}
          className="text-sm font-medium text-slate-800 hover:text-blue-600 transition line-clamp-2 leading-snug flex-1 mb-3"
          title={product.title}
        >
          {product.title}
        </Link>

        {/* Customer Reviews Rating */}
        <div className="flex items-center space-x-1 mb-3 text-xs text-slate-500">
          <div className="flex items-center text-amber-500">
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
            <span className="font-semibold text-slate-700 ml-1">4.2</span>
          </div>
          <span>•</span>
          <span>{product.review_count?.toLocaleString() || 0} reviews</span>
        </div>

        {/* Price Information in ₹ INR */}
        <div className="flex items-baseline space-x-2 pt-2 border-t border-slate-100">
          <span className="text-lg font-bold text-slate-900 font-sans">
            {product.formatted_price || `₹${product.price_inr?.toLocaleString()}`}
          </span>
          {product.price_usd && (
            <span className="text-xs text-slate-400">
              (${product.price_usd.toFixed(2)})
            </span>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-3 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between gap-2">
        <Link
          to={`/products/${product.product_id}`}
          className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline px-2 py-1"
        >
          View Details
        </Link>
        <button
          onClick={() => addToCart(product.product_id, 1)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center space-x-1 shadow-sm transition active:scale-95"
        >
          <ShoppingBag className="w-3.5 h-3.5" />
          <span>Add to Cart</span>
        </button>
      </div>
    </div>
  );
}
