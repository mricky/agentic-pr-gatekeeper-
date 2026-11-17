# Enterprise Engineering Architecture Guidelines (Quality & Safety Gates)

## 1. Concurrency & Data Consistency
- **Row-Level Locking:** All financial balances, inventory reservations, and quota allocations must use row-level locking (`SELECT FOR UPDATE`) or serializable transactions.
- **Idempotency:** All mutating webhook/API endpoints must enforce idempotent request processing using `Idempotency-Key` headers paired with payload hashing.
- **Race Condition Prevention:** State changes (e.g., ticket status `PENDING` -> `PAID`) must verify preconditions atomically.

## 2. Database Performance Standards
- **Zero N+1 Queries:** Database queries must never be triggered inside iterative application loops. Batch fetch via `IN` clauses, joins, or ORM prefetching.
- **Index Optimization:** All high-frequency `WHERE` filter clauses and join foreign keys must be backed by appropriate composite B-Tree indexes.
- **Sort Disk Spills:** Sorting operations on datasets exceeding 1,000 rows must utilize supporting indexes or appropriate memory allocation to avoid disk spills.

## 3. Reliability & Testing
- **Branch Coverage:** Minimum 80% test coverage threshold required for production merges.
- **Regression Unit Tests:** Every bug fix Pull Request must include an automated regression unit test that validates the failure scenario prior to the fix.

## 4. Security & Compliance
- **Zero Secrets:** Never hardcode secrets, private credentials, or API keys in source code.
- **SQL Injection Prevention:** All dynamic database interactions must utilize parameterized queries or safe ORM mappings.
- **Timing Attacks:** Cryptographic signature validations (e.g., HMAC-SHA256 webhooks) must employ timing-safe comparison (`hmac.compare_digest`).
