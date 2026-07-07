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