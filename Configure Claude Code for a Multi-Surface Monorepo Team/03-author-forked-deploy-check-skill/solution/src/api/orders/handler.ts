import { ApiError } from "@/api/_lib/error";
import type { ApiRequest, ApiResponse } from "@/api/_lib/types";
import { orderCreateSchema } from "@/api/_schemas/orders";
import { ordersRepo } from "@/db/orders";

interface OrderCreateBody {
  userId: string;
  items: Array<{ productId: string; quantity: number }>;
}

interface OrderCreateResponse {
  orderId: string;
  totalCents: number;
}

export async function handle(
  req: ApiRequest<OrderCreateBody>,
): Promise<ApiResponse<OrderCreateResponse>> {
  const body = orderCreateSchema.parse(req.body);

  if (body.items.length === 0) {
    throw new ApiError(400, "EMPTY_ORDER", "an order must contain at least one item");
  }

  const created = await ordersRepo.create({
    userId: body.userId,
    items: body.items,
  });

  return {
    status: 201,
    body: { orderId: created.id, totalCents: created.totalCents },
  };
}
