import type { CartItem } from "@/types/cart";
import { useEffect, useMemo, useState } from "react";
import { fetchCart } from "@/api/client";

interface MiniCartProps {
  userId: string;
}

export default function MiniCart({ userId }: MiniCartProps) {
  const [items, setItems] = useState<CartItem[]>([]);

  useEffect(() => {
    fetchCart(userId).then(setItems);
  }, [userId]);

  const itemCount = useMemo(() => items.reduce((acc, item) => acc + item.quantity, 0), [items]);
  const total = useMemo(
    () => items.reduce((acc, item) => acc + item.priceCents * item.quantity, 0),
    [items],
  );

  return (
    <div aria-label="Mini cart">
      <span>{itemCount} items</span>
      <span>${(total / 100).toFixed(2)}</span>
    </div>
  );
}
