import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ShoppingBag, Heart, Star, Sparkles, Truck, ShieldCheck, RotateCcw, ArrowLeft, Check, Layers } from 'lucide-react';
import api from '../services/api';
import ProductCard from '../components/ProductCard';
import MLWorkflowCard from '../components/MLWorkflowCard';
import { useShop } from '../context/ShopContext';

export default function ProductDetailPage() {
  const { id } = useParams();
  const { addToCart, addToWishlist, removeFromWishlist, isInWishlist } = useShop();

  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [recsLoading, setRecsLoading] = useState(true);
  const [error, setError] = useState(null);

  const isWishlisted = product ? isInWishlist(product.product_id) : false;

  useEffect(() => {
    window.scrollTo(0, 0);
    fetchProductAndRecs(id);
  }, [id]);

  const fetchProductAndRecs = async (productId) => {
    setLoading(true);
    setRecsLoading(true);
    setError(null);
    try {
      // 1. Fetch product details
      const prodRes = await api.getProductById(productId);
      setProduct(prodRes.data);
      setLoading(false);

      // 2. Fetch ML Recommendations
      try {
        const recsRes = await api.getRecommendations(productId, 6);
        setRecommendations(recsRes.data || []);
      } catch (recErr) {
        console.error('Failed to load recommendations:', recErr);
      } finally {
        setRecsLoading(false);
      }
    } catch (err) {
      console.error('Error fetching product:', err);
      setError('Product not found or unavailable.');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-sm text-slate-500">Loading product & computing similarity vectors...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h2 className="text-xl font-bold text-slate-800 mb-2">{error || 'Product Not Found'}</h2>
        <p className="text-xs text-slate-500 mb-6">The requested product identifier does not exist in the catalog.</p>
        <Link to="/products" className="bg-blue-600 text-white text-xs font-semibold px-4 py-2 rounded-lg">
          Back to Catalog
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back button */}
      <Link to="/products" className="inline-flex items-center text-xs font-medium text-slate-500 hover:text-slate-800 mb-6">
        <ArrowLeft className="w-3.5 h-3.5 mr-1" />
        Back to Products Catalog
      </Link>

      {/* Main Product Showcase */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-10 shadow-sm mb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          
          {/* Left Column: Visual Category Card */}
          <div className="flex flex-col items-center justify-center bg-gradient-to-br from-slate-100 to-blue-50/50 rounded-2xl p-8 border border-slate-200/80 min-h-[350px]">
            <div className="w-24 h-24 rounded-2xl bg-white shadow-md border border-slate-200 flex items-center justify-center text-4xl font-extrabold text-blue-600 font-sans mb-4">
              ₹
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-100/80 px-3 py-1 rounded-full mb-2">
              {product.category}
            </span>
            <span className="text-xs font-mono text-slate-400">ID: {product.product_id}</span>
            <div className="mt-6 flex items-center space-x-2 text-xs text-slate-500">
              <Check className="w-4 h-4 text-emerald-500" />
              <span>Genuine Amazon Product Record</span>
            </div>
          </div>

          {/* Right Column: Information, Pricing, & Actions */}
          <div className="flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">
                {product.category}
              </span>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mt-1 mb-3 leading-snug">
                {product.title}
              </h1>

              {/* Review Stars & Engagement */}
              <div className="flex items-center space-x-2 mb-4 text-xs text-slate-600">
                <div className="flex items-center text-amber-500">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span className="font-bold text-slate-800 ml-1">4.3</span>
                </div>
                <span>•</span>
                <span>{product.review_count?.toLocaleString()} customer reviews</span>
                <span>•</span>
                <span className="text-emerald-700 font-medium">In Stock</span>
              </div>

              {/* Price in ₹ INR & USD */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 mb-6">
                <div className="flex items-baseline space-x-3">
                  <span className="text-3xl font-extrabold text-slate-900 font-sans">
                    {product.formatted_price}
                  </span>
                  <span className="text-xs text-slate-400">
                    (${product.price_usd?.toFixed(2)} USD)
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Inclusive of all taxes. Free Indian shipping on all orders.
                </p>
              </div>

              {/* Quantity Selector and Purchase Actions */}
              <div className="flex flex-wrap items-center gap-4 mb-6">
                <div className="flex items-center border border-slate-300 rounded-xl bg-white shadow-sm">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="px-3 py-2 text-slate-600 hover:text-slate-900 text-sm font-bold"
                  >
                    -
                  </button>
                  <span className="px-3 py-2 text-sm font-semibold text-slate-800 min-w-[36px] text-center">
                    {quantity}
                  </span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="px-3 py-2 text-slate-600 hover:text-slate-900 text-sm font-bold"
                  >
                    +
                  </button>
                </div>

                <button
                  onClick={() => addToCart(product.product_id, quantity)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-6 py-3 rounded-xl shadow-md transition flex items-center justify-center space-x-2 active:scale-95"
                >
                  <ShoppingBag className="w-4 h-4" />
                  <span>Add to Cart</span>
                </button>

                <button
                  onClick={() => isWishlisted ? removeFromWishlist(product.product_id) : addToWishlist(product.product_id)}
                  className={`p-3 rounded-xl border transition ${
                    isWishlisted ? 'border-rose-300 bg-rose-50 text-rose-600' : 'border-slate-300 text-slate-500 hover:text-rose-500'
                  }`}
                  title={isWishlisted ? "In Wishlist" : "Save to Wishlist"}
                >
                  <Heart className={`w-5 h-5 ${isWishlisted ? 'fill-rose-500' : ''}`} />
                </button>
              </div>

              {/* Guarantees */}
              <div className="grid grid-cols-3 gap-2 pt-4 border-t border-slate-100 text-center text-[11px] text-slate-500">
                <div className="p-2 bg-slate-50 rounded-lg">
                  <Truck className="w-4 h-4 text-blue-600 mx-auto mb-1" />
                  <span>Free Delivery</span>
                </div>
                <div className="p-2 bg-slate-50 rounded-lg">
                  <RotateCcw className="w-4 h-4 text-amber-600 mx-auto mb-1" />
                  <span>7 Days Return</span>
                </div>
                <div className="p-2 bg-slate-50 rounded-lg">
                  <ShieldCheck className="w-4 h-4 text-emerald-600 mx-auto mb-1" />
                  <span>100% Verified</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Machine Learning Pipeline Explainer */}
      <MLWorkflowCard />

      {/* Similar Products Recommendation Shelf */}
      <div className="mt-12">
        <div className="flex items-center space-x-2 mb-6">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-bold text-slate-900">Similar Products You May Like</h2>
          <span className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full font-bold ml-2">
            Top-6 Cosine Similarity Matches
          </span>
        </div>

        {recsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 bg-slate-200/70 rounded-xl animate-pulse"></div>
            ))}
          </div>
        ) : recommendations.length === 0 ? (
          <p className="text-sm text-slate-500 italic">No similar products found for this item.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {recommendations.map((rec) => (
              <ProductCard key={rec.product_id} product={rec} showSimilarity={true} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
