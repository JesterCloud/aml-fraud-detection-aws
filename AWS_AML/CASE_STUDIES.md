# Case Studies — AML Risk Decisions

## Case 1 — Clean transaction (TXN001) **Score: 0 → ✅ APPROVE**
| Customer | CUST101 |
| Amount | $250.00 |
| Signals triggered | None |

No risk signals detected.
known location, IP matches the billing address, the account has clean history and the amount is within normal range for this customer profile.

The majority of legitimate transactions look like — no friction, no delay, straight through.

## Case 2 — Velocity attack (TXN008) **Score: 35 →   REVIEW**
| Customer | CUST108 |
| Amount | $320.00 |
| Signals triggered | `high_velocity`, `new_account` |

Two signals stacking here. The account was created recently (no trust history) and is already generating an unusual number of transactions in a short window.

Typical of account takeover fraud — a fraudster creates a fresh account and immediately starts testing it with multiple transactions before the
real owner notices. Not enough to block, but enough to flag for a human to review.

## Case 3 — Identity mismatch (TXN004) **Score: 65 → 3DS_REQUIRED**
| Customer | CUST104 |
| Amount | $3,200.00 |
| Signals triggered | `geo_mismatch`, `ip_billing_mismatch`, `high_velocity`, `high_amount` |

Four signals, high amount. The card is registered in one country, the payment is coming from another, the IP doesn't match the billing address, and there'sunusual velocity on the account.

Maybe someone traveling, using a VPN, or making a large purchase. All four together on a $3,200 transaction is a different story. We don't block yet because there's no chargeback history, but we challenge the customer with 3DS to confirm they're the legitimate cardholder.

## Case 4 — High-risk profile (TXN007) **Score: 105 → 🚨 BLOCK**
| Customer | CUST107 |
| Amount | $12,000.00 |
| Signals triggered | `geo_mismatch`, `ip_billing_mismatch`, `high_velocity`, `vpn_usage`, `chargeback_history`, `high_amount` |

Six out of seven signals. This customer has prior chargebacks meaning they've already been involved in fraudulent activity before. On top of that, they're using a VPN to mask their location, the transaction amount is $12,000, and everything about the request looks like it's coming from a different identity than the account owner.
In a real production system, this customer profile would also be flagged fo SAR filing review (Suspicious Activity Report) under AML regulations.

Mule account or compromised card scenario.

## Signal combinations that matter most
Not all signals carry equal weight. These combinations are the ones that appear most frequently in real fraud cases:

`chargeback_history` + `high_amount` = Repeat offender, testing limits
`geo_mismatch` + `ip_billing_mismatch` + `vpn_usage` =  Card not present fraud
`new_account` + `high_velocity` =  Account takeover or synthetic identity
`high_velocity` + `high_amount` + `chargeback_history` = Organized fraud ring