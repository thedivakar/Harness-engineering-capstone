interface ProcessRefundInput {
  paymentId: string;
  amountCents: number;
  reason: string;
}

export async function processRefund(input: ProcessRefundInput): Promise<string> {
  const response = await fetch(`${process.env.PAYMENT_API_URL}/refunds`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${process.env.PAYMENT_API_KEY}`,
    },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    throw new Error(`payment service rejected refund: ${response.status}`);
  }
  const { id } = (await response.json()) as { id: string };
  return id;
}
