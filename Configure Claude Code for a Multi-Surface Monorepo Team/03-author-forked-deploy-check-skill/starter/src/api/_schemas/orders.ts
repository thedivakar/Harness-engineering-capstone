import { z } from "zod";

export const orderCreateSchema = z.object({
  userId: z.string().min(1),
  items: z
    .array(
      z.object({
        productId: z.string().min(1),
        quantity: z.number().int().min(1),
      }),
    )
    .min(1),
});

export const refundRequestSchema = z.object({
  orderId: z.string().min(1),
  amountCents: z.number().int().min(1),
  reason: z.string().min(1).max(500),
});
