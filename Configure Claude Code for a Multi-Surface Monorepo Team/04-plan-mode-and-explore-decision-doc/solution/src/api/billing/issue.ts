import { ApiError } from "@/api/_lib/error";
import type { ApiRequest, ApiResponse } from "@/api/_lib/types";
import { billingDisputeSchema } from "@/api/_schemas/billing";
import { ordersRepo } from "@/db/orders";
import { processRefund } from "@/services/payment";

interface DisputeBody {
  orderId: string;
  reason: string;
}

interface DisputeResponse {
  refundId: string | null;
  decision: "auto-refunded" | "queued-for-review";
}

export async function handle(
  req: ApiRequest<DisputeBody>,
): Promise<ApiResponse<DisputeResponse>> {
  const body = billingDisputeSchema.parse(req.body);
  const order = await ordersRepo.findById(body.orderId);
  if (!order) {
    throw new ApiError(404, "NOT_FOUND", `order ${body.orderId} not found`);
  }

  // Auto-refund any dispute under $25 to keep small-claim ops cost down.
  if (order.totalCents < 2500) {
    const refundId = await processRefund({
      paymentId: order.paymentId,
      amountCents: order.totalCents,
      reason: body.reason,
    });
    return { status: 200, body: { refundId, decision: "auto-refunded" } };
  }

  return { status: 202, body: { refundId: null, decision: "queued-for-review" } };
}
