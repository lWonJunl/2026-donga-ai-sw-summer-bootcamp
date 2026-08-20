# Week 02 Day 02 - SQL JOIN, UNION and Indexes

> 원본 강의자료: `week02day02.pdf` (38쪽)

## 학습 목표

- 업무 질문에 따라 기준 테이블과 JOIN 종류를 선택한다.
- `LEFT JOIN`의 `NULL`을 미구매, 미배송, 미작성 상태로 해석한다.
- MySQL에서 FULL OUTER JOIN을 에뮬레이션한다.
- `UNION`과 `UNION ALL`을 목적과 성능에 따라 구분한다.
- 인덱스와 `EXPLAIN`으로 JOIN 비용을 확인한다.

## 실습 데이터 구조

| 테이블 | 역할 | 주요 연결 키 |
| --- | --- | --- |
| `member_info` | 회원 목록 | `member_id` |
| `purchase_info` | 주문 원장 | `member_id`, `product_id` |
| `product_info` | 상품 마스터 | `product_id` |
| `delivery_info` | 배송 상태 | `purchase_id`, `member_id` |
| `review_info` | 구매 리뷰 | `purchase_id` |
| `board_posts` | 고객 문의 | `member_id` |

`delivery_info`는 주문 상태를 배송 상태로 변환해 주문 원장과 배송 데이터의 누락이나 불일치를 비교하는 데 사용한다.

## JOIN 선택

| 질문 | 적합한 방식 |
| --- | --- |
| 양쪽에 실제로 존재하는 거래만 필요한가? | `INNER JOIN` |
| 회원 전체처럼 기준 목록을 보존해야 하는가? | 기준 테이블에서 `LEFT JOIN` |
| 오른쪽 목록을 보존해야 하는가? | 테이블 순서를 바꾼 `LEFT JOIN` 권장 |
| 양쪽 누락을 모두 찾아야 하는가? | FULL JOIN 또는 MySQL 에뮬레이션 |

`LEFT JOIN`에서 오른쪽 컬럼이 `NULL`이면 기준 목록에는 있지만 연결 데이터가 없다는 뜻이다. 이를 이용해 다음 대상을 찾을 수 있다.

- 구매 이력이 없는 활성 회원
- 배송 레코드가 없는 주문
- 리뷰가 작성되지 않은 구매
- 연결 주문이 없는 배송 문의

오른쪽 테이블의 필터를 `WHERE`에 두면 `NULL` 행이 제거되어 결과가 `INNER JOIN`처럼 줄어들 수 있다. 기준 목록을 보존해야 한다면 연결 조건을 `ON`에 둘지 검토한다.

## FULL JOIN과 집합 연산

MySQL은 FULL OUTER JOIN 문법을 직접 지원하지 않으므로 양방향 OUTER JOIN을 합치는 방식으로 구현한다.

```sql
SELECT o.purchase_id, d.delivery_status
FROM purchase_info AS o
LEFT JOIN delivery_info AS d ON d.purchase_id = o.purchase_id
UNION
SELECT o.purchase_id, d.delivery_status
FROM purchase_info AS o
RIGHT JOIN delivery_info AS d ON d.purchase_id = o.purchase_id;
```

| 연산 | 중복 처리 | 주요 용도 |
| --- | --- | --- |
| `UNION` | 중복 제거 | 최종 통합 목록, FULL JOIN 에뮬레이션 |
| `UNION ALL` | 중복 유지 | 로그, 이벤트 타임라인, 추천 신호의 중간 결과 |

`JOIN`은 서로 다른 컬럼을 한 행에 붙이고, `UNION`은 같은 구조의 행을 아래로 이어 붙인다. `UNION ALL`은 정렬이나 해시를 이용한 중복 제거가 없어 일반적으로 더 빠르다.

## 집계 활용

추천 신호처럼 출처가 다른 데이터를 `UNION ALL`로 모은 뒤 회원과 카테고리별로 집계할 수 있다.

- `SUM(score)`: 추천 점수 합계
- `COUNT(*)`: 신호 개수
- `GROUP_CONCAT(DISTINCT signal_type)`: 추천 이유
- `HAVING`: 일정 점수 이상의 후보만 선택

## 인덱스와 실행 계획

JOIN의 속도는 문법 이름보다 각 단계에서 읽는 후보 행 수에 크게 좌우된다.

- JOIN 키를 복합 인덱스의 앞쪽 컬럼으로 둔다.
- 날짜나 상태 조건으로 먼저 행 수를 줄인다.
- 기본키와 UNIQUE 키로 한 행을 직접 연결한다.
- 컬럼을 함수로 감싸거나 서로 다른 타입을 비교해 인덱스가 무효화되지 않도록 한다.

`EXPLAIN`에서는 다음 항목을 확인한다.

| 항목 | 확인 기준 |
| --- | --- |
| `type` | `ALL`보다 `ref`, `range`, `eq_ref`가 유리하다. |
| `key` | 예상한 인덱스가 선택되었는지 확인한다. |
| `rows` | 단계별 예상 읽기량이 과도하지 않은지 본다. |
| `Extra` | 불필요한 `filesort`나 큰 임시 결과를 점검한다. |

## 관련 실습 파일

- [`Join Union Practice.sql`](Join%20Union%20Practice.sql): JOIN과 UNION 실습
- [`shopping_mall_practice.sql`](shopping_mall_practice.sql): 쇼핑몰 관계형 데이터 실습

