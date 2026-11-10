-- ============================================================
--  ASSIGNMENT 02 — Joins
--  Database : BikeStores
-- ============================================================


-- ============================================================
--  Question 1
--  Retrieve the product_name, list_price, and category_name
--  for every product.
--  Use production.products and production.categories.
--  Sort the results by product_name ascending.
-- ============================================================

-- Write your query below:
SELECT p.product_name, p.list_price, c.category_name
FROM production.products p
INNER JOIN production.categories c
ON p.category_id = c.category_id
ORDER BY p.product_name;



-- ============================================================
--  Question 2
--  Show the customer full name (as full_name), order_id,
--  and order_date for all customers who have placed an order.
--  Use sales.customers and sales.orders.
--  Sort by order_date descending.
-- ============================================================

-- Write your query below:
SELECT c.first_name || ' ' || c.last_name AS "Full Name", o.order_id, o.order_date
FROM sales.customers c
INNER JOIN sales.orders o
ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC;



-- ============================================================
--  Question 3
--  Retrieve product_name, list_price, category_name, and
--  brand_name for every product.
--  Use production.products, production.categories,
--  and production.brands.
--  Sort by brand_name then product_name (both ascending).
-- ============================================================

-- Write your query below:
SELECT b.brand_name, p.product_name, p.list_price, c.category_name
FROM production.categories c
INNER JOIN production.products p
ON c.category_id = p.category_id
INNER JOIN production.brands b
ON p.brand_id = b.brand_id
ORDER BY b.brand_name, p.product_name;



-- ============================================================
--  Question 4
--  List all products along with their order_id and item_id.
--  Make sure products that have NEVER been ordered also appear
--  in the result (those rows will have NULL for order_id
--  and item_id).
--  Use production.products and sales.order_items.
--  Sort by order_id ascending.
-- ============================================================

-- Write your query below:
SELECT p.product_name, oi.order_id, oi.item_id
FROM production.products p
LEFT JOIN sales.order_items oi
ON p.product_id = oi.product_id
ORDER BY oi.order_id;



-- ============================================================
--  Question 5
--  Using your answer from Question 4 as a base, filter the
--  results to show ONLY the products that have never been
--  ordered.
--  Display only product_id and product_name.
-- ============================================================

-- Write your query below:
SELECT p.product_id, p.product_name, oi.order_id, oi.item_id
FROM production.products p
LEFT JOIN sales.order_items oi
ON p.product_id = oi.product_id
WHERE oi.order_id IS NULL;



-- ============================================================
--  Question 6
--  Show all stores along with any orders placed at each store.
--  Display store_name, store_id (from stores), order_id,
--  and order_date.
--  Every store must appear in the result, even if it has
--  no orders yet.
--  Use sales.orders and sales.stores.
-- ============================================================

-- Write your query below:
SELECT st.store_id, st.store_name, o.order_id, o.order_date
FROM sales.stores st
LEFT JOIN sales.orders o
ON st.store_id = o.store_id;





-- ============================================================
--  Question 7
--  List every staff member alongside their manager's name.
--  Display:
--    • staff full name   (as staff_name)
--    • manager full name (as manager_name)
--  Use only the sales.staffs table.
--  Staff who have no manager should NOT appear in the result.
-- ============================================================

-- Write your query below:
SELECT s.first_name || ' ' || s.last_name AS staff_name, m.first_name || ' ' || m.last_name AS manager_name
FROM sales.staffs s
INNER JOIN sales.staffs m
ON m.staff_id = s.manager_id;

SELECT *
FROM sales.staffs;


-- ============================================================
--  Question 8
--  Generate every possible combination of store name and
--  brand name.
--  Display store_name and brand_name.
--  Use sales.stores and production.brands.
--  How many total rows do you expect?
--  Write the expected count as a comment next to your query.
-- ============================================================

-- Write your query below:

SELECT store_name, brand_name
FROM sales.stores
CROSS JOIN production.brands;

-- 27 Rows Returned

SELECT *
FROM sales.stores;

SELECT *
FROM production.brands;
-- ============================================================
--  Question 9
--  Retrieve the customer full name (as full_name), order_id,
--  order_date, product_name, and list_price for every order
--  that has been placed.
--  Use sales.customers, sales.orders, sales.order_items,
--  and production.products.
--  Sort by order_date ascending, then full_name ascending.
-- ============================================================

-- Write your query below:
SELECT o.order_id, c.first_name || ' ' || c.last_name AS full_name, o.order_date, p.product_name, p.list_price
FROM sales.customers c
INNER JOIN sales.orders o
	ON c.customer_id = o.customer_id
INNER JOIN sales.order_items oi
	ON o.order_id = oi.order_id
INNER JOIN production.products p
	ON oi.product_id = p.product_id
ORDER BY o.order_date, full_name;