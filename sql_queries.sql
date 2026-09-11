-- Retail Analytics SQL queries
-- Load retail_sales.csv into a table named retail_sales.

-- Monthly revenue and units
SELECT strftime('%Y-%m', date) AS month,
       ROUND(SUM(revenue), 2) AS revenue,
       SUM(units_sold) AS units
FROM retail_sales
GROUP BY month
ORDER BY month;

-- Product performance
SELECT product,
       SUM(units_sold) AS units_sold,
       ROUND(SUM(revenue), 2) AS revenue,
       ROUND(AVG(discount), 3) AS avg_discount
FROM retail_sales
GROUP BY product
ORDER BY revenue DESC;

-- Regional performance
SELECT region,
       ROUND(SUM(revenue), 2) AS revenue,
       SUM(units_sold) AS units_sold
FROM retail_sales
GROUP BY region
ORDER BY revenue DESC;

-- Products with above-average revenue
SELECT product, ROUND(SUM(revenue), 2) AS revenue
FROM retail_sales
GROUP BY product
HAVING SUM(revenue) > (SELECT AVG(product_revenue)
                       FROM (SELECT SUM(revenue) AS product_revenue
                             FROM retail_sales GROUP BY product))
ORDER BY revenue DESC;
