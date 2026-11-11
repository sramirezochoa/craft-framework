---
capability: order-cancellation
status: active
owner: orders-team
last-verified: 2026-11-05
---

# Capability: Order cancellation

> **Worked example.** Note that it reads as a description of the system *today*
> — present tense, no history in the body. The history lives in the change log
> table at the bottom, one line per change.

## Purpose

Lets a customer stop an order they no longer want, and returns their money,
without contacting support.

## Current behaviour

Cancellation is requested through `POST /orders/{id}/cancel`. What happens
depends on the order's status.

- When an order is in `PLACED` or `PAID`, the system shall accept the
  cancellation, set its status to `CANCELLED`, issue a full refund
  synchronously, and publish `order.cancelled.v1`.
- When an order is in `SHIPPED` and fewer than 24 hours have passed since
  `shippedAt`, the system shall accept the request, set its status to
  `CANCELLATION_REQUESTED`, publish `order.cancellation_requested.v1`, and
  start a carrier recall. No refund is issued at this point.
- When a carrier recall is confirmed, the system shall set the order to
  `CANCELLED` and issue the refund.
- If the carrier recall fails or the goods are delivered anyway, the order
  returns to `DELIVERED` and the customer is directed to the returns flow.
- In every other case the system shall reject the request with HTTP 409 and
  code `ORDER_NOT_CANCELLABLE`, leaving the order unchanged.

### Rules and constraints

- The post-shipment window is configurable via
  `orders.cancellation.post-ship-window`, default `PT24H`, measured from
  `shippedAt`.
- Post-shipment cancellation is gated by the `post-ship-cancellation` flag,
  currently enabled for EU regions only.
- Refunds always go to the original payment method. Partial refunds are not
  supported here.
- An order in `CANCELLATION_REQUESTED` cannot be cancelled again.

### Failure behaviour

- Payment provider unavailable during refund: the cancellation is persisted and
  the refund retried with exponential backoff for 24 hours, then alerted.
- Carrier recall API unavailable: the request is queued and retried; if it is
  still failing after the window closes, the order falls back to `DELIVERED`.
- Concurrent cancellation requests are resolved by optimistic locking on the
  order version; the loser receives HTTP 409.

## Interfaces

| Kind | Identifier | Notes |
|---|---|---|
| HTTP | `POST /orders/{id}/cancel` | 200 immediate, 202 pending recall, 409 refused |
| Event | `order.cancelled.v1` | Published on final cancellation |
| Event | `order.cancellation_requested.v1` | Published when a recall starts |
| Event (consumed) | `carrier.recall_confirmed.v1` | Drives the transition to `CANCELLED` |

## Where it lives

| Concern | Location |
|---|---|
| Entry point | `src/main/java/.../web/OrderCancellationController.java` |
| Core logic | `src/main/java/.../orders/OrderCancellationService.java` |
| Recall integration | `src/main/java/.../carrier/RecallClient.java` |
| Persistence | `src/main/java/.../orders/OrderRepository.java` |
| Tests | `src/test/java/.../orders/OrderCancellationTest.java` |

## Dependencies

- **Payments** — refunds. Unavailable: cancellation still succeeds, refund retried.
- **Carrier integration** — recall. Unavailable: request queued, falls back to returns.
- **Order history UI** — renders `CANCELLATION_REQUESTED`.

## Not in scope

- **Partial cancellation** of individual line items — not supported anywhere.
- **Returns after delivery** — a separate capability, `returns`.
- **Subscription cancellation** — `subscription-lifecycle`.

## Open questions

*(none)*

## Change log

| Change | Date | Summary |
|---|---|---|
| [012](012-allow-cancel-after-ship/change.md) | 2026-11-05 | Allowed cancellation within 24h of shipment, via carrier recall |
| [004](#) | 2026-08-12 | Added synchronous refund on cancellation |
| [001](#) | 2026-06-02 | Initial cancellation for PLACED and PAID orders |
