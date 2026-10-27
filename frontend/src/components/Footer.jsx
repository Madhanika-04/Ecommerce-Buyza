import React from 'react';
import { ShieldCheck, Truck, RotateCcw, Cpu, Sparkles } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 mt-20 border-t border-slate-800">
      {/* Trust Badges Bar */}
      <div className="bg-slate-950 py-6 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="flex flex-col items-center">
            <Truck className="w-6 h-6 text-blue-400 mb-2" />
            <h4 className="text-white text-xs font-bold uppercase tracking-wider">Pan-India Delivery</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Fast shipping to all 28 states & 8 UTs</p>
          </div>
          <div className="flex flex-col items-center">
            <ShieldCheck className="w-6 h-6 text-emerald-400 mb-2" />
            <h4 className="text-white text-xs font-bold uppercase tracking-wider">Simulated Checkout</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Zero real payment card data collected</p>
          </div>
          <div className="flex flex-col items-center">
            <RotateCcw className="w-6 h-6 text-amber-400 mb-2" />
            <h4 className="text-white text-xs font-bold uppercase tracking-wider">7-Day Replacement</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Hassle-free return policy</p>
          </div>
          <div className="flex flex-col items-center">
            <Cpu className="w-6 h-6 text-purple-400 mb-2" />
            <h4 className="text-white text-xs font-bold uppercase tracking-wider">TF-IDF & Cosine Similarity</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Genuine ML content-based recommendations</p>
          </div>
        </div>
      </div>

      {/* Main Footer Details */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center space-x-2 text-white font-bold text-lg mb-3">
              <span className="w-7 h-7 bg-blue-600 rounded flex items-center justify-center text-sm">₹</span>
              <span>E-Commerce Recommendation System</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              An academic Data Science & Full-Stack engineering project integrating genuine Machine Learning (TF-IDF vectorization and sparse Cosine Similarity) with FastAPI and React.
            </p>
            <div className="inline-flex items-center text-xs bg-slate-800 text-blue-400 px-3 py-1.5 rounded-full border border-slate-700">
              <Sparkles className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
              76,327 Cleaned Products Indexed
            </div>
          </div>

          <div>
            <h4 className="text-white text-sm font-semibold mb-3">Retail Departments</h4>
            <ul className="text-xs space-y-2">
              <li>Laptops & Computers</li>
              <li>Mobiles & Tablets</li>
              <li>Cameras & Photography</li>
              <li>Audio & Video</li>
              <li>Men's Fashion & Footwear</li>
              <li>Toys & Games</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white text-sm font-semibold mb-3">Project Architecture</h4>
            <ul className="text-xs space-y-2">
              <li>FastAPI REST Backend (Uvicorn / Pydantic)</li>
              <li>MongoDB Persistence (Cart, Wishlist, Orders)</li>
              <li>Scikit-Learn Sparse TF-IDF Vectorizer</li>
              <li>Query-Specific Cosine Similarity Engine</li>
              <li>Tailwind CSS & React Router</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-8 pt-6 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} E-Commerce Recommendation System. Academic Project.</p>
          <p className="mt-2 sm:mt-0">Built for Indian E-Commerce with genuine data.</p>
        </div>
      </div>
    </footer>
  );
}
