import type { CartItem } from "@/types/cart";
import { useEffect, useMemo, useState } from "react";
import { fetchCart, updateQuantity } from "@/api/client";

interface CartProps {
  userId: string;
  onCheckout: (items: CartItem[]) => void;
}

export default function Cart({ userId, onCheckout }: CartProps) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetchCart(userId).then((next) => {
      if (active) {
        setItems(next);
        setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, [userId]);

  const total = useMemo(
    () => items.reduce((acc, item) => acc + item.priceCents * item.quantity, 0),
    [items],
  );

  function setQuantity(productId: string, quantity: number) {
    updateQuantity(userId, productId, quantity).then((next) => setItems(next));
  }

  if (loading) return <div>Loading cart…</div>;

  return (
    <section aria-label="Shopping cart">
      <ul>
        {items.map((item) => (
          <li key={item.productId}>
            <span>{item.name}</span>
            <input
              type="number"
              min={0}
              value={item.quantity}
              onChange={(e) => setQuantity(item.productId, Number(e.target.value))}
            />
          </li>
        ))}
      </ul>
      <button type="button" onClick={() => onCheckout(items)}>
        Checkout (${(total / 100).toFixed(2)})
      </button>
    </section>
  );
}
