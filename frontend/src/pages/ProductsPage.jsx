import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Filter, SlidersHorizontal, Search, ArrowLeft, ArrowRight, RotateCcw } from 'lucide-react';
import api from '../services/api';
import ProductCard from '../components/ProductCard';
import { useShop } from '../context/ShopContext';

export default function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { categories } = useShop();

  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filter States
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const selectedCategory = searchParams.get('category') || '';
  const searchKeyword = searchParams.get('search') || '';
  const sortBy = searchParams.get('sort_by') || '';
  const minPrice = searchParams.get('min_price') || '';
  const maxPrice = searchParams.get('max_price') || '';

  const [searchInput, setSearchInput] = useState(searchKeyword);
  const [minPriceInput, setMinPriceInput] = useState(minPrice);
  const [maxPriceInput, setMaxPriceInput] = useState(maxPrice);

  useEffect(() => {
    fetchProducts();
  }, [searchParams]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        page_size: 20,
      };
      if (selectedCategory) params.category = selectedCategory;
      if (searchKeyword) params.search = searchKeyword;
      if (sortBy) params.sort_by = sortBy;
      if (minPrice) params.min_price = parseInt(minPrice, 10);
      if (maxPrice) params.max_price = parseInt(maxPrice, 10);

      const res = await api.getProducts(params);
      setProducts(res.data.items || []);
      setTotal(res.data.total || 0);
      setTotalPages(res.data.total_pages || 1);
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateParam = (key, value) => {
    const nextParams = new URLSearchParams(searchParams);
    if (value !== '' && value !== null && value !== undefined) {
      nextParams.set(key, value);
    } else {
      nextParams.delete(key);
    }
    // Reset to page 1 on filter changes
    if (key !== 'page') nextParams.set('page', '1');
    setSearchParams(nextParams);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    updateParam('search', searchInput.trim());
  };

  const handlePriceApply = () => {
    const nextParams = new URLSearchParams(searchParams);
    if (minPriceInput) nextParams.set('min_price', minPriceInput);
    else nextParams.delete('min_price');
    if (maxPriceInput) nextParams.set('max_price', maxPriceInput);
    else nextParams.delete('max_price');
    nextParams.set('page', '1');
    setSearchParams(nextParams);
  };

  const handleResetFilters = () => {
    setSearchInput('');
    setMinPriceInput('');
    setMaxPriceInput('');
    setSearchParams({});
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-200 mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            {selectedCategory ? selectedCategory : 'Product Catalog'}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Showing {products.length} of {total.toLocaleString()} products in ₹ INR
          </p>
        </div>

        {/* Sorting Dropdown */}
        <div className="flex items-center space-x-3">
          <label htmlFor="sort-select" className="text-xs font-semibold text-slate-600">Sort By:</label>
          <select
            id="sort-select"
            value={sortBy}
            onChange={(e) => updateParam('sort_by', e.target.value)}
            className="bg-white border border-slate-300 rounded-lg text-xs font-medium px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-sm"
          >
            <option value="">Default (Relevance)</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="reviews_desc">Most Reviewed / Popular</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-6 sticky top-24">
            
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="font-bold text-sm text-slate-900 flex items-center">
                <Filter className="w-4 h-4 mr-2 text-blue-600" /> Filters
              </span>
              {(selectedCategory || searchKeyword || sortBy || minPrice || maxPrice) && (
                <button
                  onClick={handleResetFilters}
                  className="text-xs text-rose-600 hover:text-rose-700 font-semibold flex items-center"
                >
                  <RotateCcw className="w-3 h-3 mr-1" /> Reset
                </button>
              )}
            </div>

            {/* Keyword Search Filter */}
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-2">Search Catalog</label>
              <form onSubmit={handleSearchSubmit} className="flex">
                <input
                  type="text"
                  placeholder="Keyword..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-l-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-3 rounded-r-lg text-xs flex items-center justify-center hover:bg-blue-700"
                >
                  <Search className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>

            {/* Category Filter */}
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-2">Departments</label>
              <div className="space-y-1 max-h-56 overflow-y-auto pr-1">
                <button
                  onClick={() => updateParam('category', '')}
                  className={`w-full text-left text-xs px-2.5 py-1.5 rounded-lg transition ${
                    !selectedCategory ? 'bg-blue-600 text-white font-semibold' : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  All Departments ({total.toLocaleString()})
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat.category}
                    onClick={() => updateParam('category', cat.category)}
                    className={`w-full text-left text-xs px-2.5 py-1.5 rounded-lg transition flex justify-between items-center ${
                      selectedCategory === cat.category
                        ? 'bg-blue-600 text-white font-semibold'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <span className="truncate">{cat.category}</span>
                    <span className="text-[10px] opacity-75">{cat.product_count}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Price Filter (₹ INR) */}
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-2">Price Range (₹ INR)</label>
              <div className="flex items-center space-x-2 mb-2">
                <input
                  type="number"
                  placeholder="Min ₹"
                  value={minPriceInput}
                  onChange={(e) => setMinPriceInput(e.target.value)}
                  className="w-1/2 bg-slate-50 border border-slate-300 rounded-lg text-xs px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <span className="text-slate-400 text-xs">-</span>
                <input
                  type="number"
                  placeholder="Max ₹"
                  value={maxPriceInput}
                  onChange={(e) => setMaxPriceInput(e.target.value)}
                  className="w-1/2 bg-slate-50 border border-slate-300 rounded-lg text-xs px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={handlePriceApply}
                className="w-full bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold py-1.5 rounded-lg transition"
              >
                Apply Price Filter
              </button>
            </div>
          </div>
        </div>

        {/* Product Grid & Pagination */}
        <div className="lg:col-span-3">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {[...Array(9)].map((_, i) => (
                <div key={i} className="h-64 bg-slate-200/70 rounded-xl animate-pulse"></div>
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
              <p className="text-base font-semibold text-slate-700">No products found matching your filters.</p>
              <p className="text-xs text-slate-500 mt-1 mb-4">Try clearing some search keywords or price restrictions.</p>
              <button
                onClick={handleResetFilters}
                className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition"
              >
                Clear All Filters
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {products.map((product) => (
                  <ProductCard key={product.product_id} product={product} />
                ))}
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t border-slate-200 mt-10 pt-6">
                  <button
                    disabled={currentPage <= 1}
                    onClick={() => updateParam('page', currentPage - 1)}
                    className="flex items-center space-x-1 px-4 py-2 rounded-lg border border-slate-300 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    <ArrowLeft className="w-3.5 h-3.5" />
                    <span>Previous</span>
                  </button>

                  <div className="text-xs text-slate-600">
                    Page <span className="font-bold text-slate-900">{currentPage}</span> of{' '}
                    <span className="font-bold text-slate-900">{totalPages.toLocaleString()}</span>
                  </div>

                  <button
                    disabled={currentPage >= totalPages}
                    onClick={() => updateParam('page', currentPage + 1)}
                    className="flex items-center space-x-1 px-4 py-2 rounded-lg border border-slate-300 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    <span>Next</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
