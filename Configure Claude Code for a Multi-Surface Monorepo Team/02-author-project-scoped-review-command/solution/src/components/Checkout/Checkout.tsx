import type { CartItem } from "@/types/cart";
import { useEffect, useMemo, useState } from "react";
import { fetchCart, submitOrder } from "@/api/client";

interface CheckoutProps {
  userId: string;
}

export default function Checkout({ userId }: CheckoutProps) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCart(userId).then(setItems);
  }, [userId]);

  const total = useMemo(
    () => items.reduce((acc, item) => acc + item.priceCents * item.quantity, 0),
    [items],
  );

  async function placeOrder() {
    setSubmitting(true);
    await submitOrder(userId, items);
    setSubmitting(false);
  }

  return (
    <section aria-label="Checkout">
      <h1>Review your order</h1>
      <ul>
        {items.map((item) => (
          <li key={item.productId}>
            {item.name} × {item.quantity}
          </li>
        ))}
      </ul>
      <p>Total: ${(total / 100).toFixed(2)}</p>
      <button type="button" disabled={submitting} onClick={placeOrder}>
        {submitting ? "Placing order…" : "Place order"}
      </button>
    </section>
  );
}
