use Chapter02Day01;

-- ---------------------------------------------------------------------------
-- 하나의 테이블에서 SELECT 구조 설명 예제
-- ---------------------------------------------------------------------------

-- 1. 전체 데이터 일부 조회
SELECT
  order_id,
  order_no,
  customer_name,
  product_name,
  quantity,
  total_amount,
  order_status,
  ordered_at
FROM order_details
ORDER BY order_id
LIMIT 20;

-- 2. WHERE 조건 조회: VIP 고객의 완료 주문
SELECT
  order_id,
  customer_name,
  customer_grade,
  product_name,
  total_amount,
  order_status
FROM order_details
WHERE customer_grade = 'VIP'
  AND order_status = 'DELIVERED'
ORDER BY total_amount DESC;

-- 3. ORDER BY + LIMIT: 주문금액 TOP 20
SELECT
  order_id,
  customer_name,
  product_category,
  product_name,
  total_amount
FROM order_details
ORDER BY total_amount DESC
LIMIT 20;

-- 4. GROUP BY: 고객등급별 주문 통계
SELECT
  customer_grade,
  COUNT(*) AS order_count,
  SUM(total_amount) AS total_sales,
  ROUND(AVG(total_amount), 0) AS avg_order_amount
FROM order_details
GROUP BY customer_grade
ORDER BY total_sales DESC;

-- 5. GROUP BY + HAVING: 매출 500,000원 이상 카테고리
SELECT
  product_category,
  COUNT(*) AS order_count,
  SUM(quantity) AS sold_quantity,
  SUM(total_amount) AS total_sales
FROM order_details
WHERE order_status IN ('PAID', 'SHIPPED', 'DELIVERED')
GROUP BY product_category
HAVING SUM(total_amount) >= 500000
ORDER BY total_sales DESC;

-- 6. WHERE 안의 단일값 서브쿼리: 평균 주문금액보다 큰 주문
SELECT
  order_id,
  customer_name,
  product_name,
  total_amount
FROM order_details
WHERE total_amount > (
  SELECT AVG(total_amount)
  FROM order_details
)
ORDER BY total_amount DESC
LIMIT 20;

-- 7. IN 서브쿼리: 전자기기 구매 이력이 있는 고객의 모든 주문
SELECT
  order_id,
  customer_id,
  customer_name,
  product_category,
  product_name,
  total_amount
FROM order_details
WHERE customer_id IN (
  SELECT DISTINCT customer_id
  FROM order_details
  WHERE product_category = '전자기기'
)
ORDER BY customer_id, order_id;

-- 8. 상관 서브쿼리: 고객별 총 구매금액을 주문 행마다 함께 표시
SELECT
  od.order_id,
  od.customer_id,
  od.customer_name,
  od.product_name,
  od.total_amount,
  (
    SELECT SUM(inner_od.total_amount)
    FROM order_details inner_od
    WHERE inner_od.customer_id = od.customer_id
  ) AS customer_total_amount
FROM order_details od
ORDER BY customer_total_amount DESC, od.order_id
LIMIT 30;

-- 9. EXISTS: 같은 고객이 100,000원 이상 주문을 한 번이라도 가진 주문만 조회
SELECT
  od.order_id,
  od.customer_name,
  od.product_name,
  od.total_amount
FROM order_details od
WHERE EXISTS (
  SELECT 1
  FROM order_details high_od
  WHERE high_od.customer_id = od.customer_id
    AND high_od.total_amount >= 100000
)
ORDER BY od.customer_id, od.order_id;

-- 10. 파생 테이블: 고객별 주문 요약을 만든 뒤 TOP 20 조회
SELECT
  customer_summary.customer_id,
  customer_summary.customer_name,
  customer_summary.customer_grade,
  customer_summary.order_count,
  customer_summary.total_sales,
  customer_summary.avg_order_amount
FROM (
  SELECT
    customer_id,
    MAX(customer_name) AS customer_name,
    MAX(customer_grade) AS customer_grade,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_sales,
    ROUND(AVG(total_amount), 0) AS avg_order_amount
  FROM order_details
  GROUP BY customer_id
) AS customer_summary
ORDER BY customer_summary.total_sales DESC
LIMIT 20;

-- 11. CTE: 카테고리별 매출 요약을 이름 붙여 재사용
WITH category_sales AS (
  SELECT
    product_category,
    COUNT(*) AS order_count,
    SUM(quantity) AS sold_quantity,
    SUM(total_amount) AS total_sales
  FROM order_details
  WHERE order_status IN ('PAID', 'SHIPPED', 'DELIVERED')
  GROUP BY product_category
)
SELECT
  product_category,
  order_count,
  sold_quantity,
  total_sales
FROM category_sales
WHERE total_sales >= 500000
ORDER BY total_sales DESC;

-- 12. CASE 표현식: 주문금액 구간별 분류
SELECT
  CASE
    WHEN total_amount >= 300000 THEN '고액 주문'
    WHEN total_amount >= 100000 THEN '중간 주문'
    ELSE '일반 주문'
  END AS amount_group,
  COUNT(*) AS order_count,
  SUM(total_amount) AS total_sales
FROM order_details
GROUP BY amount_group
ORDER BY total_sales DESC;