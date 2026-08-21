"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function PremiumPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [entitlements, setEntitlements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [prods, ents] = await Promise.all([
        api.get<any>("/api/payments/products"),
        api.get<any>("/api/payments/entitlements"),
      ]);
      setProducts(prods.products || []);
      setEntitlements(ents.entitlements || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (productId: number) => {
    setPurchasing(productId);
    try {
      const order = await api.post<any>("/api/payments/create-order", { product_id: productId });

      // Load Razorpay script
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => {
        const options = {
          key: order.key_id,
          amount: order.amount * 100,
          currency: order.currency,
          name: "Niksmind",
          description: order.product_name,
          order_id: order.order_id,
          handler: async function (response: any) {
            try {
              await api.post("/api/payments/verify", {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                product_id: productId,
              });
              alert("Payment successful! Premium content unlocked.");
              loadData();
            } catch (err: any) {
              alert("Payment verification failed: " + err.message);
            }
          },
          prefill: { name: "", email: "" },
          theme: { color: "#7c3aed" },
        };
        const rzp = new (window as any).Razorpay(options);
        rzp.open();
      };
      document.body.appendChild(script);
    } catch (err: any) {
      alert(err.message || "Failed to initiate payment");
    } finally {
      setPurchasing(null);
    }
  };

  const hasEntitlement = (certId: number) => {
    return entitlements.some((e) => e.status === "active");
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Upgrade to Premium</h1>
        <p className="text-gray-600 mt-1">Unlock the full certification preparation experience</p>
      </div>

      {/* Features comparison */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 mb-8">
        <h2 className="font-semibold text-gray-900 mb-4">What&apos;s Included in Premium</h2>
        <div className="grid grid-cols-2 gap-4">
          {[
            "50 Additional Premium MCQs per topic",
            "Advanced scenario-based questions",
            "Detailed explanations",
            "Full Mock Exams",
            "Advanced Analytics",
            "Flashcards with AI generation",
            "Adaptive Learning",
            "AI Tutor",
            "Personalized Study Plan",
            "Priority support",
          ].map((feature) => (
            <div key={feature} className="flex items-center gap-2 text-sm">
              <span className="text-green-500">✓</span>
              <span className="text-gray-700">{feature}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Products */}
      <div className="grid gap-6">
        {products.map((product) => (
          <div key={product.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">{product.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{product.description}</p>
              <div className="mt-2 text-2xl font-bold text-purple-600">
                ₹{product.price}
                <span className="text-sm font-normal text-gray-500">/{product.currency}</span>
              </div>
            </div>
            <button
              onClick={() => handlePurchase(product.id)}
              disabled={purchasing === product.id}
              className="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {purchasing === product.id ? "Processing..." : "Unlock Premium"}
            </button>
          </div>
        ))}
      </div>

      {products.length === 0 && (
        <div className="text-center text-gray-500 py-12">
          <p>No premium products available yet.</p>
        </div>
      )}
    </div>
  );
}
