import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, ShoppingBag, Trash2, ArrowRight } from 'lucide-react';
import { useShop } from '../context/ShopContext';

export default function WishlistPage() {
  const { wishlist, removeFromWishlist, addToCart } = useShop();

  const handleMoveToCart = async (productId) => {
    await addToCart(productId, 1);
    await removeFromWishlist(productId);
  };

  if (wishlist.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="w-16 h-16 bg-rose-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-rose-200">
          <Heart className="w-8 h-8 text-rose-500" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Your Wishlist is Empty</h2>
        <p className="text-sm text-slate-500 mb-8 max-w-sm mx-auto">
          Save your favourite items by tapping the heart icon on any product card or details page.
        </p>
        <Link
          to="/products"
          className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-6 py-3 rounded-xl shadow-md transition"
        >
          <span>Explore Products</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between pb-6 border-b border-slate-200 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center">
            <Heart className="w-6 h-6 mr-2 text-rose-500 fill-rose-500" />
            My Saved Wishlist
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            {wishlist.total_items} item{wishlist.total_items === 1 ? '' : 's'} saved for later
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {wishlist.items.map((item) => (
          <div
            key={item.product_id}
            className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between"
          >
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full">
                {item.category}
              </span>
              <Link
                to={`/products/${item.product_id}`}
                className="block text-sm font-semibold text-slate-800 hover:text-blue-600 mt-2 mb-2 line-clamp-2"
              >
                {item.title}
              </Link>
              <div className="text-base font-bold text-slate-900 font-sans mb-4">
                {item.formatted_price}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
              <button
                onClick={() => removeFromWishlist(item.product_id)}
                className="text-slate-400 hover:text-rose-600 p-2 transition"
                title="Remove"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleMoveToCart(item.product_id)}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-2 rounded-lg flex items-center justify-center space-x-1 transition"
              >
                <ShoppingBag className="w-3.5 h-3.5" />
                <span>Move to Cart</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
