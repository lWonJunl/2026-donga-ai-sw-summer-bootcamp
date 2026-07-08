use Chapter02Day02;

-- 1.1. 회원별 주문 및 리뷰 상태 조회 1
SELECT m.member_id, m.member_name,
    COUNT(p.purchase_id) AS orders,
    COUNT(r.review_id) AS reviews
FROM member_info m
LEFT JOIN purchase_info p ON p.member_id = m.member_id
LEFT JOIN review_info r ON r.purchase_id = p.purchase_id
GROUP BY m.member_id, m.member_name;

-- 1.2. 회원별 주문 및 리뷰 상태 조회 2
SELECT m.member_name,
    COUNT(p.purchase_id) AS orders,
    COUNT(r.review_id) AS reviews
FROM member_info m
LEFT JOIN purchase_info p ON p.member_id = m.member_id
LEFT JOIN review_info r ON r.purchase_id = p.purchase_id
GROUP BY m.member_name;

-- 2. 배송 문의와 주문 상태 연결
SELECT b.post_id, b.member_id, p.purchase_id, p.purchase_status
FROM board_posts b
LEFT JOIN purchase_info p
ON p.member_id = b.member_id
AND p.purchased_at >= DATE_SUB(b.created_at, INTERVAL 30 DAY)
WHERE b.board_category = '배송';

-- 
SELECT
    m.member_id,m.member_name,m.email, m.member_grade,
    p.purchase_id, p.purchased_at, p.purchase_status,
    p.quantity, p.total_amount,
    d.delivery_status, d.carrier, d.tracking_no,
    pr.product_id, pr.product_name, pr.category, pr.price,
    r.rating, r.review_content
FROM member_info m
JOIN purchase_info p
ON p.member_id = m.member_id
JOIN product_info pr
ON pr.product_id = p.product_id
LEFT JOIN delivery_info d
ON d.purchase_id = p.purchase_id
LEFT JOIN review_info r
ON r.purchase_id = p.purchase_id
WHERE m.member_name = '이서연'
ORDER BY p.purchased_at DESC;

-- INDEX를 활용한 조회
SELECT * FROM member_info WHERE member_id = 10;

-- 내용을 이용한 조회
SELECT * FROM member_info WHERE member_name = '이서연';

SELECT
    m.member_id,m.member_name,m.email, m.member_grade,
    p.purchase_id, p.purchased_at, p.purchase_status,
    p.quantity, p.total_amount,
    d.delivery_status, d.carrier, d.tracking_no,
    pr.product_id, pr.product_name, pr.category, pr.price,
    r.rating, r.review_content
FROM member_info m
JOIN purchase_info p
ON p.member_id = m.member_id
JOIN product_info pr
ON pr.product_id = p.product_id
LEFT JOIN delivery_info d
ON d.purchase_id = p.purchase_id
LEFT JOIN review_info r
ON r.purchase_id = p.purchase_id
WHERE m.member_name = '이서연'
ORDER BY p.purchased_at DESC;

EXPLAIN
SELECT
    p.purchase_id,
    p.purchased_at,
    m.member_name,
    p.purchase_status,
    d.delivery_status,
    r.rating
FROM purchase_info p
JOIN member_infom
ON m.member_id = p.member_id
LEFT JOIN delivery_info d
ON d.purchase_id = p.purchase_id
LEFT JOIN review_info r
ON r.member_id = p.member_id
AND r.created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
WHERE p.purchased_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY p.purchased_at DESC, m.member_nameASC;