# TransitMatrix - Advanced SQL Query Demonstrations Catalog

This catalog documents the 21 meaningful SQL queries designed and implemented for the TransitMatrix database. All queries execute against the implemented MySQL schema (`transitmatrix`) populated with the seed dataset.

---

## Query Index & Classification

| Query File | Description | Core SQL Concept |
|---|---|---|
| `q01_multi_table_inner_join.sql` | Passenger journey manifest joining 8 tables | Multi-table INNER JOIN |
| `q02_left_outer_join.sql` | Station route origin census including terminals | LEFT OUTER JOIN & GROUP_CONCAT |
| `q03_nested_subquery_scalar.sql` | Trips with base fare above overall network average | Scalar nested subquery in WHERE |
| `q04_nested_subquery_in.sql` | Travelers on high-speed Rajdhani or Vande Bharat | IN predicate subquery |
| `q05_correlated_subquery_select.sql` | Route summary with correlated delay counts & averages | Correlated subquery in SELECT |
| `q06_correlated_subquery_exists.sql` | Train services experiencing major delays (> 40 mins) | Correlated EXISTS predicate |
| `q07_correlated_subquery_not_exists.sql` | Inactive registered passengers with zero bookings | Correlated NOT EXISTS predicate |
| `q08_aggregate_group_by.sql` | Booking metrics and fare stats by service type | Aggregates (COUNT, SUM, AVG, MIN, MAX) |
| `q09_group_by_having.sql` | High-incident stations with chronic delays | GROUP BY with HAVING clause |
| `q10_common_table_expression_cte.sql` | Route net revenue calculation after refunds | Common Table Expressions (WITH clause) |
| `q11_recursive_cte_graph_path.sql` | Multi-hop transit path traversal from New Delhi | Recursive CTE (Graph Reachability) |
| `q12_window_row_number.sql` | Ranking tickets by fare within coach class | `ROW_NUMBER() OVER (PARTITION BY ...)` |
| `q13_window_dense_rank.sql` | Top grossing routes ranked without gaps | `DENSE_RANK() OVER (ORDER BY ...)` |
| `q14_window_running_total.sql` | Progressive cumulative daily revenue & 7-day average | Running totals and rolling frame windows |
| `q15_window_lag_lead.sql` | Inter-train departure spacing on routes | `LAG()` and `LEAD()` analytic functions |
| `q16_query_on_view_availability.sql` | Query on `v_trip_availability` for high occupancy | Analytical query on view |
| `q17_query_on_view_performance.sql` | Query on `v_route_performance` for route ranking | Operational query on view |
| `q18_transaction_commit_locking.sql` | Pessimistic locking reservation transaction | Row locking (`FOR UPDATE`) & COMMIT |
| `q19_transaction_rollback.sql` | Concurrency collision handling and atomic rollback | Intentional error check & ROLLBACK |
| `q20_stored_procedure_and_trigger.sql` | Journey search and cancellation procedure audit | Stored procedure CALL & trigger audit |
| `q21_index_explain_analysis.sql` | Query execution plan inspection on B-Tree indexes | `EXPLAIN` query plan analysis |

---

## Detailed Query Specifications

### Q01: Multi-Table Inner Join
- **Business Question:** Retrieve complete traveler journey manifests with seat numbers, coach codes, travel classes, train numbers, origin and destination station names, and booking status.
- **Tables Joined:** `bookings`, `tickets`, `passengers`, `trips`, `services`, `routes`, `stations` (as origin and destination), `seats`.
- **Expected Result:** A tabular manifest of confirmed journeys ordered chronologically.

### Q05: Correlated Subquery in SELECT
- **Business Question:** For every route, dynamically compute the total scheduled trips, total delay incidents recorded, and average delay duration in minutes.
- **Mechanism:** Inner subquery references outer table attribute `r.route_id` to filter delays.

### Q06 & Q07: EXISTS & NOT EXISTS
- **Q06 (EXISTS):** Checks for existence of at least one row in `delays` joined with `trips` for each service.
- **Q07 (NOT EXISTS):** Set-difference query identifying registered users in the `users` table who do not have any corresponding records in `bookings`.

### Q10: Common Table Expression (CTE)
- **Business Question:** Break down complex multi-table revenue computations into modular blocks (`RouteGrossRevenue` and `RouteRefunds`) and join them to calculate net revenue after cancellations.

### Q11: Recursive CTE Graph Reachability
- **Business Question:** Model the railway network as a directed graph where stations are nodes and routes are edges. Recursively explore all paths up to 2 hops starting from New Delhi (NDLS), accumulating travel distance.

### Q12 - Q15: Window Functions
- **Q12 (`ROW_NUMBER()`):** Numerically indexes tickets partitioned by trip and coach class.
- **Q13 (`DENSE_RANK()`):** Ranks routes by total booking revenue without leaving gaps between ranks.
- **Q14 (`SUM() OVER ...`):** Calculates running cumulative revenue over time.
- **Q15 (`LAG()` and `LEAD()`):** Computes time difference between consecutive train departures on each corridor.

### Q18 & Q19: ACID Transactions and Concurrency
- **Q18:** Starts a transaction, acquires exclusive row lock on seat inventory via `SELECT ... FOR UPDATE`, marks the seat unavailable, inserts booking and ticket records, and commits.
- **Q19:** Demonstrates that if a seat is unavailable, issuing `ROLLBACK` guarantees that no orphaned booking records are written to disk.

### Q20: Stored Procedure & Trigger Auditing
- Executes `sp_search_trips` to find available trains between NDLS and BCT.
- Calls `sp_cancel_booking` with an OUT parameter, verifying that trigger `trg_cancellation_after_insert` automatically frees the seat and creates an audit entry in `audit_logs`.

### Q21: EXPLAIN Query Plan Analysis
- Analyzes the execution plan of filtered range queries against index `idx_trips_route_date_status`. Shows that MySQL performs an index range scan rather than a full table scan.

