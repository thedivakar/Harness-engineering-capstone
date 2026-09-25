import { z } from "zod";

export const billingDisputeSchema = z.object({
  orderId: z.string().min(1),
  reason: z.string().min(1).max(500),
});
