---
change: 012
title: Allow cancellation after shipment
status: merged
track: full
capabilities: [order-cancellation]
author: example
reviewer: example
created: 2026-11-03
merged: 2026-11-05
---

# Change 012 — Allow cancellation after shipment

> **This is a worked example**, kept in `framework/example/` so it does not
> pollute a real project's change history. It shows the level of detail a good
> change spec carries. Delete the folder once your own changes exist.

## Why

Support handles roughly 40 cancellation requests a week for orders that have
just shipped. Today these are refused by the system and resolved manually by
raising a return, which takes about ten minutes each and confuses customers
who cancelled within minutes of the shipping email.

The owner wants these handled automatically inside a short window.

## Current behaviour

Verified against `OrderCancellationService` and `OrderStatus`:

- Cancellation is accepted only while an order is in `PLACED` or `PAID`.
- When the order is in any other status, `POST /orders/{id}/cancel` returns
  HTTP 409 with code `ORDER_NOT_CANCELLABLE`, and the order is unchanged.
- A successful cancellation sets status to `CANCELLED`, publishes
  `order.cancelled.v1`, and triggers a refund synchronously.
- The shipment timestamp is recorded on the order as `shippedAt` but is not
  currently used by the cancellation path.

## Desired behaviour

- Cancellation is also accepted for `SHIPPED` orders, within 24 hours of
  `shippedAt`.
- Because the goods are already in transit, a post-shipment cancellation does
  not refund immediately. It records the intent and starts the carrier recall
  process; the refund follows when the recall is confirmed.
- Customers outside the window continue to be refused as today.

## What does NOT change

- Cancellation behaviour for `PLACED` and `PAID` orders, including the
  synchronous refund.
- The error code and HTTP status for refusals.
- The `order.cancelled.v1` event schema.
- Orders in `DELIVERED`, `CANCELLED` or `REFUNDED` remain non-cancellable.

## Acceptance criteria

| ID | Criterion |
|---|---|
| AC-1 | When an order with status SHIPPED is cancelled within 24 hours of `shippedAt`, the system shall set its status to `CANCELLATION_REQUESTED` and return HTTP 202. |
| AC-2 | When an order with status SHIPPED is cancelled more than 24 hours after `shippedAt`, the system shall return HTTP 409 with code `ORDER_NOT_CANCELLABLE` and leave the order unchanged. |
| AC-3 | When an order enters `CANCELLATION_REQUESTED`, the system shall publish `order.cancellation_requested.v1` and shall not issue a refund. |
| AC-4 | While an order is in `CANCELLATION_REQUESTED`, the system shall reject further cancellation requests with HTTP 409. |
| AC-5 | When a carrier recall is confirmed for an order in `CANCELLATION_REQUESTED`, the system shall set its status to `CANCELLED` and issue the refund. |

## Behaviour changes to existing tests or evals

| Test / eval | Current assertion | New assertion | Why |
|---|---|---|---|
| `OrderCancellationTest.shippedOrderCannotBeCancelled` | SHIPPED always returns 409 | Returns 409 only outside the 24h window | The rule this test encodes is exactly what this change alters |

## Out of scope

- Partial cancellation of individual line items — separate change.
- Carrier recall for carriers that do not support it; those orders fall back to
  the existing returns flow. Tracked as a follow-up.
- Customer-facing copy in the mobile app.

## Impact

| Area | Impact |
|---|---|
| Capabilities touched | `order-cancellation` |
| Contracts | New event `order.cancellation_requested.v1`; `POST /orders/{id}/cancel` may now return 202 |
| Data / migrations | New `OrderStatus` value `CANCELLATION_REQUESTED`; no schema migration |
| Configuration | New `orders.cancellation.post-ship-window` (default `PT24H`) |
| Clients affected | Order history UI must render the new status |
| Rollout | Behind flag `post-ship-cancellation`, enabled per region |

## Open questions

*(none — all resolved before approval)*

## Decisions needing an ADR

- Whether the refund is driven by the carrier recall callback or by a scheduled
  reconciliation job → ADR 0008.
