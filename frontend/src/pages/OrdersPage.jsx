import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Package, Clock, CheckCircle2, MapPin, ArrowRight } from 'lucide-react';
import api from '../services/api';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await api.getOrders('guest_user');
      setOrders(res.data || []);
    } catch (err) {
      console.error('Failed to load orders:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-sm text-slate-500">Loading order history...</p>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-200">
          <Package className="w-8 h-8 text-slate-400" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-2">No Orders Found</h2>
        <p className="text-sm text-slate-500 mb-8 max-w-sm mx-auto">
          You haven't placed any simulated orders yet. Browse our catalog and test out the simulated checkout flow!
        </p>
        <Link
          to="/products"
          className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-6 py-3 rounded-xl shadow-md transition"
        >
          <span>Start Shopping</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="pb-6 border-b border-slate-200 mb-8">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center">
          <Package className="w-6 h-6 mr-2 text-blue-600" />
          My Orders & History
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          {orders.length} order{orders.length === 1 ? '' : 's'} placed (Simulated)
        </p>
      </div>

      <div className="space-y-6">
        {orders.map((order) => (
          <div
            key={order.order_id}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            {/* Order Header */}
            <div className="bg-slate-50/80 px-6 py-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center space-x-3">
                <span className="font-mono font-bold text-slate-800 text-sm">{order.order_id}</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                  {order.status}
                </span>
              </div>
              <div className="text-slate-500 flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>{new Date(order.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
              </div>
            </div>

            {/* Line Items */}
            <div className="p-6 divide-y divide-slate-100">
              {order.items.map((item, idx) => (
                <div key={idx} className="py-3 first:pt-0 last:pb-0 flex justify-between items-center text-xs">
                  <div className="flex-1 pr-4">
                    <span className="font-semibold text-slate-800 block line-clamp-1">{item.title}</span>
                    <span className="text-[11px] text-slate-500">
                      Qty: {item.quantity} • {item.formatted_price} each
                    </span>
                  </div>
                  <span className="font-bold text-slate-900 font-sans text-sm">
                    {item.formatted_subtotal}
                  </span>
                </div>
              ))}
            </div>

            {/* Order Footer with Delivery Address and Total */}
            <div className="bg-slate-50/50 px-6 py-4 border-t border-slate-200 flex flex-wrap justify-between items-center gap-4 text-xs">
              <div className="flex items-start space-x-2 text-slate-600 max-w-md">
                <MapPin className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Delivery to:</strong> {order.delivery_address.full_name}, {order.delivery_address.address_line}, {order.delivery_address.city}, {order.delivery_address.state} - {order.delivery_address.pin_code}
                </span>
              </div>

              <div className="flex items-baseline space-x-2">
                <span className="text-slate-500 font-medium">Grand Total:</span>
                <span className="text-lg font-extrabold text-blue-600 font-sans">
                  {order.formatted_total}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
