import type { Order, OrderCreate } from "@/db/types";
import { pool } from "@/db/pool";
import type { Tx } from "@/db/tx";

export const ordersRepo = {
  async findById(orderId: string): Promise<Order | null> {
    const { rows } = await pool.query<Order>(
      "SELECT id, user_id, payment_id, total_cents, refunded_id FROM orders WHERE id = $1",
      [orderId],
    );
    return rows[0] ?? null;
  },

  async create(input: OrderCreate): Promise<Order> {
    const totalCents = input.items.reduce(
      (acc, item) => acc + item.priceCents * item.quantity,
      0,
    );
    const { rows } = await pool.query<Order>(
      `INSERT INTO orders (user_id, total_cents)
       VALUES ($1, $2)
       RETURNING id, user_id, payment_id, total_cents, refunded_id`,
      [input.userId, totalCents],
    );
    return rows[0];
  },

  async markRefunded(orderId: string, refundId: string, tx: Tx): Promise<void> {
    await tx.query("UPDATE orders SET refunded_id = $1 WHERE id = $2", [refundId, orderId]);
  },
};
