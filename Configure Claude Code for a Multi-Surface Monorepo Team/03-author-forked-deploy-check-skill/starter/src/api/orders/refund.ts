import { ApiError } from "@/api/_lib/error";
import type { ApiRequest, ApiResponse } from "@/api/_lib/types";
import { refundRequestSchema } from "@/api/_schemas/orders";
import { ordersRepo } from "@/db/orders";
import { withTransaction } from "@/db/tx";
import { processRefund } from "@/services/payment";

interface RefundRequestBody {
  orderId: string;
  amountCents: number;
  reason: string;
}

interface RefundResponse {
  refundId: string;
}

export async function handle(
  req: ApiRequest<RefundRequestBody>,
): Promise<ApiResponse<RefundResponse>> {
  const body = refundRequestSchema.parse(req.body);
  const order = await ordersRepo.findById(body.orderId);
  if (!order) {
    throw new ApiError(404, "NOT_FOUND", `order ${body.orderId} not found`);
  }

  const refundId = await withTransaction(async (tx) => {
    const id = await processRefund({
      paymentId: order.paymentId,
      amountCents: body.amountCents,
      reason: body.reason,
    });
    await ordersRepo.markRefunded(body.orderId, id, tx);
    return id;
  });

  return { status: 200, body: { refundId } };
}
