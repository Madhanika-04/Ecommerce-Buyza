import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingBag, Trash2, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../services/api';
import { useShop } from '../context/ShopContext';

const INDIAN_STATES = [
  "Andhra Pradesh", "Assam", "Bihar", "Delhi", "Gujarat", "Haryana",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Punjab",
  "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh", "West Bengal"
];

export default function CartPage() {
  const { cart, updateCartQuantity, removeFromCart, clearCartState, showToast } = useShop();
  const navigate = useNavigate();

  // Checkout Form State
  const [address, setAddress] = useState({
    full_name: '',
    phone: '',
    address_line: '',
    city: '',
    state: 'Karnataka',
    pin_code: '',
  });

  const [paymentMethod, setPaymentMethod] = useState('Cash on Delivery (Simulated)');
  const [submitting, setSubmitting] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  const [confirmedOrder, setConfirmedOrder] = useState(null);

  const validateForm = () => {
    const errors = {};
    if (!address.full_name.trim() || address.full_name.trim().length < 2) {
      errors.full_name = 'Name must be at least 2 characters';
    }
    const cleanPhone = address.phone.replace(/\D/g, '');
    if (cleanPhone.length !== 10) {
      errors.phone = 'Valid 10-digit Indian mobile number required';
    }
    if (!address.address_line.trim() || address.address_line.trim().length < 5) {
      errors.address_line = 'Address must be at least 5 characters';
    }
    if (!address.city.trim()) {
      errors.city = 'City is required';
    }
    if (!/^[1-9][0-9]{5}$/.test(address.pin_code.trim())) {
      errors.pin_code = 'Valid 6-digit Indian PIN code required (cannot start with 0)';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCheckoutSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitting(true);
    try {
      const orderPayload = {
        user_id: 'guest_user',
        delivery_address: {
          full_name: address.full_name.trim(),
          phone: address.phone.replace(/\D/g, ''),
          address_line: address.address_line.trim(),
          city: address.city.trim(),
          state: address.state,
          pin_code: address.pin_code.trim(),
        },
        payment_method: paymentMethod,
      };

      const res = await api.placeOrder(orderPayload);
      setConfirmedOrder(res.data);
      clearCartState();
      showToast('Order confirmed successfully!');
    } catch (err) {
      console.error('Checkout failed:', err);
      showToast(err.response?.data?.detail || 'Failed to place simulated order.');
    } finally {
      setSubmitting(false);
    }
  };

  // Order Confirmation Success View
  if (confirmedOrder) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-3xl border border-slate-200 p-8 sm:p-12 shadow-md">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 border border-emerald-300">
            <CheckCircle2 className="w-10 h-10 text-emerald-600" />
          </div>
          <span className="text-xs font-bold text-emerald-700 uppercase tracking-widest bg-emerald-50 px-3 py-1 rounded-full">
            Simulated Checkout Confirmed
          </span>
          <h2 className="text-2xl font-bold text-slate-900 mt-3 mb-1">Thank You for Your Order!</h2>
          <p className="text-xs font-mono text-slate-500 mb-6">Order ID: {confirmedOrder.order_id}</p>

          <div className="bg-slate-50 rounded-xl p-4 text-left text-xs space-y-2 border border-slate-200/80 mb-6">
            <div className="flex justify-between font-semibold text-slate-800 border-b border-slate-200 pb-2">
              <span>Items: {confirmedOrder.total_items}</span>
              <span>Total: {confirmedOrder.formatted_total}</span>
            </div>
            <div>
              <span className="text-slate-500">Delivery Address:</span>
              <p className="font-medium text-slate-800">
                {confirmedOrder.delivery_address.full_name}, {confirmedOrder.delivery_address.address_line}, {confirmedOrder.delivery_address.city}, {confirmedOrder.delivery_address.state} - {confirmedOrder.delivery_address.pin_code}
              </p>
            </div>
            <div>
              <span className="text-slate-500">Payment:</span> {confirmedOrder.payment_method}
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            <Link
              to="/orders"
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-6 py-2.5 rounded-xl shadow-md transition"
            >
              View All Orders
            </Link>
            <Link
              to="/products"
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-6 py-2.5 rounded-xl transition"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Empty Cart View
  if (cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-200">
          <ShoppingBag className="w-8 h-8 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Your Shopping Cart is Empty</h2>
        <p className="text-sm text-slate-500 mb-8 max-w-sm mx-auto">
          Explore India's verified product catalog and add electronics, fashion, or footwear to your cart.
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
      <h1 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
        <ShoppingBag className="w-6 h-6 mr-2 text-blue-600" />
        Shopping Cart & Checkout ({cart.total_items} items)
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Cart Line Items (2/3) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100 shadow-sm overflow-hidden">
            {cart.items.map((item) => (
              <div key={item.product_id} className="p-4 sm:p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="flex-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                    {item.category}
                  </span>
                  <Link
                    to={`/products/${item.product_id}`}
                    className="block text-sm font-semibold text-slate-800 hover:text-blue-600 mt-1 line-clamp-2"
                  >
                    {item.title}
                  </Link>
                  <span className="text-xs text-slate-500 font-sans">
                    Unit Price: {item.formatted_price}
                  </span>
                </div>

                {/* Quantity Controls & Subtotal */}
                <div className="flex items-center space-x-4 self-end sm:self-center">
                  <div className="flex items-center border border-slate-300 rounded-lg bg-white">
                    <button
                      onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                      className="px-2.5 py-1 text-slate-600 hover:text-slate-900 text-xs font-bold"
                    >
                      -
                    </button>
                    <span className="px-2 text-xs font-bold text-slate-800 min-w-[28px] text-center">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                      className="px-2.5 py-1 text-slate-600 hover:text-slate-900 text-xs font-bold"
                    >
                      +
                    </button>
                  </div>

                  <span className="font-bold text-sm text-slate-900 font-sans min-w-[80px] text-right">
                    {item.formatted_subtotal}
                  </span>

                  <button
                    onClick={() => removeFromCart(item.product_id)}
                    className="text-slate-400 hover:text-rose-600 p-1"
                    title="Remove item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Order Summary & Checkout Form (1/3) */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Price Summary Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
              Price Details
            </h3>
            <div className="flex justify-between text-xs text-slate-600">
              <span>Price ({cart.total_items} items)</span>
              <span className="font-semibold text-slate-900">{cart.formatted_total}</span>
            </div>
            <div className="flex justify-between text-xs text-slate-600">
              <span>Delivery Charges</span>
              <span className="text-emerald-600 font-bold">FREE (India)</span>
            </div>
            <div className="border-t border-slate-200 pt-3 flex justify-between font-bold text-base text-slate-900">
              <span>Total Payable</span>
              <span className="text-blue-600 font-sans">{cart.formatted_total}</span>
            </div>
          </div>

          {/* Delivery Address & Simulated Checkout Form */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center">
              <ShieldCheck className="w-4 h-4 mr-1.5 text-blue-600" />
              Delivery Address (India)
            </h3>

            <form onSubmit={handleCheckoutSubmit} className="space-y-3">
              <div>
                <label className="text-[11px] font-semibold text-slate-700 block mb-1">Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. Rohan Sharma"
                  value={address.full_name}
                  onChange={(e) => setAddress({ ...address, full_name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {formErrors.full_name && <p className="text-[10px] text-rose-600 mt-0.5">{formErrors.full_name}</p>}
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-700 block mb-1">Mobile Number (+91)</label>
                <input
                  type="tel"
                  placeholder="10-digit number"
                  maxLength={10}
                  value={address.phone}
                  onChange={(e) => setAddress({ ...address, phone: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {formErrors.phone && <p className="text-[10px] text-rose-600 mt-0.5">{formErrors.phone}</p>}
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-700 block mb-1">Flat, House no., Building, Street</label>
                <input
                  type="text"
                  placeholder="Address..."
                  value={address.address_line}
                  onChange={(e) => setAddress({ ...address, address_line: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {formErrors.address_line && <p className="text-[10px] text-rose-600 mt-0.5">{formErrors.address_line}</p>}
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] font-semibold text-slate-700 block mb-1">City</label>
                  <input
                    type="text"
                    placeholder="Bengaluru"
                    value={address.city}
                    onChange={(e) => setAddress({ ...address, city: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  {formErrors.city && <p className="text-[10px] text-rose-600 mt-0.5">{formErrors.city}</p>}
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-700 block mb-1">PIN Code</label>
                  <input
                    type="text"
                    placeholder="6 digits (e.g. 560103)"
                    maxLength={6}
                    value={address.pin_code}
                    onChange={(e) => setAddress({ ...address, pin_code: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  {formErrors.pin_code && <p className="text-[10px] text-rose-600 mt-0.5">{formErrors.pin_code}</p>}
                </div>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-700 block mb-1">State</label>
                <select
                  value={address.state}
                  onChange={(e) => setAddress({ ...address, state: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {INDIAN_STATES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* Simulated Payment Selector */}
              <div className="pt-2">
                <label className="text-[11px] font-semibold text-slate-700 block mb-1">Payment Method</label>
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="Cash on Delivery (Simulated)">Cash on Delivery (Simulated)</option>
                  <option value="UPI / QR (Simulated)">UPI / QR (Simulated)</option>
                </select>
                <p className="text-[10px] text-slate-400 mt-1 italic">
                  *Academic project: No real payment information collected.
                </p>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-3 rounded-xl shadow-md transition disabled:opacity-50 active:scale-95"
              >
                {submitting ? 'Placing Order...' : `Place Simulated Order • ${cart.formatted_total}`}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
