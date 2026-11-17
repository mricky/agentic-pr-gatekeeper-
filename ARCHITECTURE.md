# 🏛️ Core Architectural Standards & Safety Invariants

## 1. Concurrency & Data Consistency
- All monetary transactions and inventory deductions must execute under row-level locks (`SELECT FOR UPDATE`) or serializable isolation.
- Webhook callbacks and financial APIs must enforce idempotent request processing via `Idempotency-Key` headers paired with cryptographic payload hashing.

## 2. Database Performance Standards
- Zero unindexed queries permitted in core transaction paths.
- N+1 query loops inside ORM iterations are strictly prohibited.
- Sorting operations on datasets > 1,000 rows must utilize supporting B-Tree indexes to prevent temporary disk spills (`work_mem`).

## 3. Testing & Reliability
- Minimum 80% branch coverage threshold required for production merges.
- All non-trivial bug fixes must be accompanied by regression unit tests.

