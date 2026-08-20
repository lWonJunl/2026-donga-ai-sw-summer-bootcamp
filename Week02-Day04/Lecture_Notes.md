# Week 02 Day 04 - PostgreSQL, PostGIS and pgRouting

> 원본 강의자료: `week02day04.pdf` (25쪽)

## 학습 목표

- PostgreSQL 설치 구성과 접속 상태를 확인한다.
- PostGIS와 pgRouting 확장을 활성화한다.
- Python `psycopg`로 공간 데이터에 접근한다.
- 건물 Polygon과 도로 그래프로 최단 경로를 계산한다.

## 설치와 기본 확인

Windows 설치 시 다음 구성요소를 확인한다.

- PostgreSQL Server: 실제 데이터베이스 엔진
- pgAdmin: GUI 관리 도구
- StackBuilder: PostGIS 같은 추가 확장 설치 도구
- 기본 포트: `5432`

설치 후 PostgreSQL 서비스가 실행 중인지 확인하고, `psql`, pgAdmin과 실습 데이터베이스 접속을 점검한다.

```sql
CREATE DATABASE gis_lab;
```

## 확장 활성화

```sql
CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;
```

PostGIS는 `geometry`, `geography`, 거리와 포함 관계 같은 공간 타입과 함수를 제공한다. pgRouting은 도로를 그래프로 보고 최단 경로를 계산하는 함수를 제공한다.

## Python 연결

서비스 코드에서는 DSN을 소스에 직접 적지 않고 환경변수로 분리한다. `with` 블록을 사용하면 연결 종료와 트랜잭션 범위를 명확히 관리할 수 있다.

```python
import os
import psycopg
from psycopg.rows import dict_row

with psycopg.connect(os.environ["GIS_LAB_DSN"], row_factory=dict_row) as conn:
    rows = conn.execute("SELECT id, name FROM buildings ORDER BY id").fetchall()
```

사용자 입력은 문자열 결합 대신 파라미터로 전달한다.

## 공간 데이터

| 타입 또는 함수 | 역할 |
| --- | --- |
| `geometry(Polygon, 4326)` | 건물 외곽 면 저장 |
| `geometry(LineString, 4326)` | 실제 도로선 저장 |
| `ST_Distance` | 두 공간 객체 사이 거리 계산 |
| `ST_DWithin` | 지정 반경 안의 후보 판별 |
| `ST_PointOnSurface` | Polygon 내부의 대표점 생성 |
| `ST_AsGeoJSON` | 웹 지도에서 사용할 GeoJSON 변환 |
| GiST index | 겹침, 포함과 근접 검색 가속 |

경위도 좌표계 `4326`의 `geometry` 거리는 degree 단위이므로 meter 거리로 해석하면 안 된다. `geography`로 변환하거나 목적에 맞는 투영 좌표계를 사용해야 한다.

## 건물과 도로 모델

건물은 `Polygon`, 도로는 `LineString`으로 저장한다. pgRouting용 도로 테이블에는 다음 값이 필요하다.

- `source`, `target`: 도로의 시작과 끝 정점
- `cost`: 정방향 이동 비용
- `reverse_cost`: 역방향 이동 비용
- `geom`: 지도에 표시할 실제 도로선

이동 비용은 거리뿐 아니라 시간, 요금, 혼잡도 점수가 될 수도 있다.

## 경로 계산 흐름

1. 건물 Polygon에서 중심점이나 출입구 대표점을 만든다.
2. GiST 인덱스를 이용해 가장 가까운 도로 정점을 찾는다.
3. `pgr_dijkstra()`로 출발 정점과 도착 정점 사이의 edge 순서를 계산한다.
4. 반환된 edge 번호를 도로 테이블과 JOIN한다.
5. `ST_AsGeoJSON()`으로 실제 도로선을 웹 지도에 전달한다.

경유지가 있으면 출발지-경유지와 경유지-도착지 구간으로 나누어 계산하고 결과를 합친다.

## 오류 점검

| 증상 | 확인 항목 |
| --- | --- |
| 거리가 비정상적임 | 좌표 순서, SRID, `geometry`와 `geography` 단위 |
| 경로가 나오지 않음 | `source`, `target`, `cost`, `reverse_cost`와 방향성 |
| 공간 조회가 느림 | GiST 인덱스와 실행 계획 |
| 확장 함수가 없음 | 현재 DB에 확장이 설치되었는지 확인 |

## 관련 실습 파일

- [`navDay02.md`](navDay02.md): 캠퍼스 길찾기 Day 2 문서
- [`navDay02.py`](navDay02.py): Python 서비스 로직
- [`navDay02.sql`](navDay02.sql): PostgreSQL 공간 데이터 실습

