# navDay02.sql 데이터 구조

`navDay02.sql`은 캠퍼스 네비게이션을 만들기 위한 장소와 경로 데이터를 저장한다. 이 데이터는 길찾기 관점에서 그래프 구조로 볼 수 있다.

```text
place_data = 장소 노드
road_data  = 장소와 장소를 잇는 간선
```

## 전체 구성

| 구분 | 내용 |
| --- | --- |
| 데이터베이스 | `nav` |
| 문자셋 | `utf8mb4` |
| Collation | `utf8mb4_unicode_ci` |
| 테이블 | `place_data`, `road_data` |
| 장소 데이터 | 128행 |
| 도로 데이터 | 30행 |
| 경로 해석 방식 | 양방향 |

스크립트는 기존 `road_data`, `place_data` 테이블을 삭제한 뒤 다시 생성하고 데이터를 삽입한다.

## 네비게이션 해석 기준

`road_data`의 한 행은 두 장소가 연결되어 있다는 뜻으로 사용한다. 실제 길찾기에서는 이 연결을 양방향으로 해석한다.

예를 들어 SQL에 아래 데이터가 있을 때:

```text
PL07 -> CR07
```

네비게이션에서는 다음 두 경로가 모두 가능하다고 본다.

```text
PL07 -> CR07
CR07 -> PL07
```

따라서 길찾기 그래프를 만들 때는 `from_place -> to_place`뿐 아니라 `to_place -> from_place`도 함께 추가해야 한다.

## 테이블 관계

```text
place_data.place_id
        ^
        |
road_data.from_place
road_data.to_place
```

`road_data.from_place`와 `road_data.to_place`는 `place_data.place_id`를 참조하는 값으로 사용한다. 현재 SQL에는 `FOREIGN KEY` 제약 조건이 직접 선언되어 있지는 않다.

## place_data

장소, 건물, 출입구, 버스정류장, 교차 지점, 주차장 등을 저장하는 테이블이다.

| 컬럼명 | 타입 | NULL | 키/인덱스 | 설명 |
| --- | --- | --- | --- | --- |
| `place_id` | `VARCHAR(255)` | 불가 | `idx_place_id` | 장소 식별자 |
| `place_name` | `VARCHAR(255)` | 가능 |  | 장소 이름 |
| `latitude` | `DOUBLE` | 가능 |  | 위도 |
| `longitude` | `DOUBLE` | 가능 |  | 경도 |
| `altitude` | `DOUBLE` | 가능 |  | 고도 |

### place_id 규칙

네비게이션 데이터에서는 `place_id`가 고유해야 한다. 하나의 장소 ID가 여러 장소를 의미하면 경로 탐색 시 어느 위치로 이동해야 하는지 모호해진다.

| 패턴 | 의미 |
| --- | --- |
| `S01`, `S02` 등 | 주요 건물 |
| `S01-01F`, `S06-06F01E` 등 | 건물의 층 또는 출입구 |
| `EL01`, `EL06` 등 | 엘리베이터 |
| `BS01`, `BS06` 등 | 버스정류장 |
| `CR01-01`, `CR05` 등 | 교차 지점 또는 연결 지점 |
| `PL00`, `PL04` 등 | 주차장 또는 기타 위치 |
| `GATE` | 정문 |

## road_data

두 장소 사이의 이동 경로를 저장하는 테이블이다.

| 컬럼명 | 타입 | NULL | 키/인덱스 | 설명 |
| --- | --- | --- | --- | --- |
| `road_id` | `INT` | 불가 | `PRIMARY KEY` | 경로 식별자, 자동 증가 |
| `from_place` | `VARCHAR(255)` | 불가 | `idx_road_from_place` | 연결된 장소 A |
| `to_place` | `VARCHAR(255)` | 불가 | `idx_road_to_place` | 연결된 장소 B |
| `road_type` | `VARCHAR(255)` | 가능 |  | 도로 유형 |
| `distance` | `INT` | 가능 |  | 거리 |
| `time` | `INT` | 가능 |  | 예상 이동 시간 |
| `indoor` | `BOOLEAN` | 불가 |  | 실내 경로 여부 |
| `stair` | `BOOLEAN` | 불가 |  | 계단 경로 여부 |
| `slope` | `INT` | 가능 |  | 경사도 |

### 경로 해석

- `from_place`와 `to_place`는 방향보다는 연결 관계를 의미한다.
- 길찾기 로직에서는 한 행을 양방향 간선으로 등록한다.
- `distance`는 거리 기반 최단 경로 계산에 사용할 수 있다.
- `time`은 시간 기반 최단 경로 계산에 사용할 수 있다.
- `indoor`, `stair`, `slope`는 경로 옵션을 만들 때 가중치로 사용할 수 있다.

예시:

```text
road_data: GATE, CR07, distance 216, time 3

그래프 등록:
GATE -> CR07
CR07 -> GATE
```

## 길찾기 가중치 예시

목적에 따라 경로 비용을 다르게 계산할 수 있다.

| 경로 옵션 | 기준 |
| --- | --- |
| 최단 거리 | `distance` |
| 최단 시간 | `time` |
| 계단 회피 | `stair = 1`인 경로에 패널티 추가 |
| 실내 우선 | `indoor = 1`인 경로를 우선하거나 실외 경로에 패널티 추가 |
| 완만한 길 | `slope`가 큰 경로에 패널티 추가 |

예시 비용:

```text
cost = time

if stair = 1:
    cost += 5

if slope is not null:
    cost += slope
```

## 인덱스

| 테이블 | 인덱스명 | 컬럼 | 목적 |
| --- | --- | --- | --- |
| `place_data` | `idx_place_id` | `place_id` | 장소 ID 검색 |
| `road_data` | `PRIMARY` | `road_id` | 경로 고유 식별 |
| `road_data` | `idx_road_from_place` | `from_place` | 연결 장소 검색 |
| `road_data` | `idx_road_to_place` | `to_place` | 연결 장소 검색 |

## 데이터 정리 기준

네비게이션으로 사용하려면 다음 조건을 만족하는 것이 좋다.

| 항목 | 기준 |
| --- | --- |
| `place_id` | 중복 없이 고유해야 함 |
| `from_place` | `place_data.place_id`에 존재해야 함 |
| `to_place` | `place_data.place_id`에 존재해야 함 |
| 도로 방향 | 양방향으로 해석 |
| 좌표 | 지도 표시가 필요한 장소는 위도와 경도가 있어야 함 |

## 현재 SQL 점검 결과

현재 파일을 기준으로 자동 점검하면 다음 항목이 확인된다.

| 항목 | 내용 |
| --- | --- |
| 장소 행 수 | 128 |
| 도로 행 수 | 30 |
| 도로 ID 범위 | `1` ~ `30` |
| 중복으로 감지된 `place_id` | `CR01-01`, `PL01`, `S11-04F01E` |
| `road_data`에서 참조하지만 `place_data`에 없는 ID | `PL01-01`, `PL03`, `S17 B1F` |

중복이 실제로 정리된 상태라면, SQL 파일의 해당 `place_id` 값이 서로 다른 고유 ID로 바뀌었는지 다시 확인하면 된다.

기본값 내위치?
출발지 도착지 맞바꾸기
경유지 추가 (단, 이동방식은 다르게 할 수도 있어야)
