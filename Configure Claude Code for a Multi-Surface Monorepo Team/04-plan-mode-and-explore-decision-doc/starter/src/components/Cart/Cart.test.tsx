import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Cart from "./Cart";

vi.mock("@/api/client", () => ({
  fetchCart: vi.fn().mockResolvedValue([
    { productId: "p1", name: "Widget", priceCents: 1500, quantity: 2 },
  ]),
  updateQuantity: vi.fn(),
}));

describe("Cart", () => {
  it("renders the loaded items with the formatted total", async () => {
    render(<Cart userId="u1" onCheckout={() => undefined} />);
    expect(await screen.findByText(/Widget/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Checkout \(\$30\.00\)/ })).toBeInTheDocument();
  });

  it("shows the loading state before items resolve", () => {
    render(<Cart userId="u1" onCheckout={() => undefined} />);
    expect(screen.getByText(/Loading cart/)).toBeInTheDocument();
  });
});
