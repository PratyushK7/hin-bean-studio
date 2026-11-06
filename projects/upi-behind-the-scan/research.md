# Research: UPI transaction ke peeche kya hota hai?

**Research checked:** 7 November 2026  
**Scope:** A normal domestic UPI payment from one bank account to another, using a third-party UPI app. Merchant payments, UPI Lite, PPI wallets, credit on UPI, mandates and cross-border variants are outside the main flow except where a caveat is useful.

## Central question
Jab user kisi UPI ID ya QR code par payment karta hai, toh app, PSP bank, NPCI aur dono banks ka role kya hota hai?

## Likely misconception
"PhonePe/Google Pay mere paise ko ek wallet se doosre wallet mein bhejta hai." This is inaccurate for the common bank-linked UPI flow. The app is the interface; the payment is connected to participating banks and the UPI network. UPI also supports other product variants, so do not claim every UPI transaction is exclusively a direct bank-account transfer.

## Simple mental model
1. **Payer / sender:** initiates the payment.
2. **UPI app / TPAP:** the interface through which the user initiates and sees the transaction. A third-party app provider operates through a PSP bank.
3. **Payer PSP:** member bank enabling the app's UPI connectivity/onboarding.
4. **NPCI / UPI switch:** network operator and central routing/orchestration layer passing transaction messages between participants.
5. **Remitter bank:** sender's bank; authenticates the UPI PIN and debits the sender's account.
6. **Beneficiary bank:** receiver's bank; credits the receiving account and returns transaction status.
7. **Payee PSP:** supports receiving-side UPI onboarding/address resolution, depending on the flow.

## Typical bank-linked payment, simplified
1. User scans a QR or selects a UPI ID and enters the amount.
2. App initiates a payment request with the relevant payment address and transaction details.
3. User approves with UPI PIN. The PIN authorizes the sender-side bank transaction.
4. The request is routed through the UPI ecosystem/NPCI to the remitter bank for authentication and debit.
5. The network routes the credit request to the beneficiary bank.
6. Beneficiary bank credits the receiving account and returns status; the app displays the result.

This is a conceptual flow, not a claim that every app's internal API sequence is identical. NPCI's participant definitions and operating circulars describe more detailed message and exception handling.

## "Instant" vs settlement
UPI is designed as an instant, 24x7 customer payment system. That customer-facing experience should not be confused with separate interbank clearing/settlement and reconciliation processes. A successful on-screen transaction does not mean every bank's back-office settlement ledger updates in the same millisecond.

NPCI's September 2025 operating circular describes separate member settlement cycles for authentication and dispute transactions, effective 3 November 2025. This is institutional settlement processing, not the consumer-facing authorization/credit sequence.

## Pending / failed payments
A pending status can occur when payer-side debit and beneficiary-side credit/status confirmation do not complete cleanly at the same time. NPCI distinguishes business declines from technical declines and describes debit-reversal cases. Avoid promising a universal refund time: handling depends on transaction status, bank and applicable rules.

## Security
- UPI PIN authorizes a payment from the sender's account; never share it.
- A collect/request-to-pay flow differs from sending money: approving a collect request can authorize a debit. Do not teach viewers to enter a PIN to receive money.
- QR code is a payment initiation aid, not proof that the recipient is trustworthy.
- Verify recipient name and amount before confirming.
- A successful payment to the wrong recipient is not automatically reversible; prevention matters.

## History
UPI launched in April 2016 and was built over IMPS infrastructure. The film focuses on architecture, not generic "UPI changed India" claims.

## Claims to avoid
- "UPI is a wallet."
- "NPCI itself holds everyone's money."
- "Money physically travels from one phone to another."
- "The app alone verifies your PIN."
- "All UPI payments are identical."
- "Every pending transaction refunds instantly."
- Any unsourced current transaction-volume statistic.

## Visual principles
Use a clean system diagram with lanes for user's app, NPCI switch, sender bank and receiver bank. Animate transaction messages and status responses; do not depict currency notes travelling through cables. Label the diagram as a simplified model. Keep transaction authorization/credit distinct from later interbank settlement.
