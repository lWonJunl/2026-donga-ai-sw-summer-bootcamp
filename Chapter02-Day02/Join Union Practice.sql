use Chapter02Day02;

-- INNER JOIN
select m.member_name, p.purchase_id, p.total_amount
from member_info m
inner join purchase_info p
on p.member_id = m.member_id
where p.purchase_status = 'DELIVERED';

-- LEFT JOIN
select m.member_name, p.purchase_id, p.total_amount
from member_info m
left join purchase_info p
on p.member_id = m.member_id
where m.is_active = 'Y';

-- FULL JOIN 1 (UNION)
SELECT o.purchase_id, d.delivery_status
FROM purchase_info o
LEFT JOIN delivery_info d ON d.purchase_id = o.purchase_id
UNION
SELECT o.purchase_id, d.delivery_status
FROM purchase_info o
RIGHT JOIN delivery_info d ON d.purchase_id = o.purchase_id;

-- FULL JOIN 2 (UNION)
SELECT o.purchase_id, d.member_id
FROM purchase_info o
LEFT JOIN member_info d ON d.member_id = o.member_id
UNION
SELECT o.purchase_id, d.member_id
FROM purchase_info o
RIGHT JOIN member_info d ON d.member_id = o.member_id;

-- FULL JOIN 3 (UNION ALL)
SELECT member_id, purchased_at AS event_at, 'ORDER' AS type
FROM purchase_info
UNION ALL
SELECT member_id, last_updated_at AS event_at, 'DELIVERY' AS type
FROM delivery_info
ORDER BY event_at DESC;