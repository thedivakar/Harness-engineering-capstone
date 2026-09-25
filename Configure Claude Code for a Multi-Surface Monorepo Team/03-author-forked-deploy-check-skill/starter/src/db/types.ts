export interface Order {
  id: string;
  userId: string;
  paymentId: string;
  totalCents: number;
  refundedId: string | null;
}

export interface OrderCreate {
  userId: string;
  items: Array<{
    productId: string;
    quantity: number;
    priceCents: number;
  }>;
}
