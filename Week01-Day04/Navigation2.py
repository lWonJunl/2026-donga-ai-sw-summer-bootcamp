import heapq

# ============================================================
# 1. 장소 데이터 POI
# 장소는 실제 목적지 후보입니다.
# 각 장소는 가장 가까운 도로 노드에 붙어 있다고 가정합니다.
# ============================================================

POI_DATA = [
    {"id": "P01", "category": "식당", "name": "김치마을", "rating": 4.6, "road_node": "J02", "access_distance": 0.08},
    {"id": "P02", "category": "주유소", "name": "북부셀프주유소", "rating": 4.1, "road_node": "J03", "access_distance": 0.12},
    {"id": "P03", "category": "카페", "name": "스타카페", "rating": 4.7, "road_node": "J01", "access_distance": 0.05},
    {"id": "P04", "category": "식당", "name": "서울칼국수", "rating": 4.2, "road_node": "J04", "access_distance": 0.10},
    {"id": "P05", "category": "카페", "name": "라떼하우스", "rating": 4.3, "road_node": "J05", "access_distance": 0.07},
    {"id": "P06", "category": "주유소", "name": "행복오일", "rating": 4.5, "road_node": "J06", "access_distance": 0.15},
    {"id": "P07", "category": "식당", "name": "동쪽분식", "rating": 4.1, "road_node": "J02", "access_distance": 0.20},
    {"id": "P08", "category": "카페", "name": "동쪽커피", "rating": 4.2, "road_node": "J07", "access_distance": 0.09},
    {"id": "P09", "category": "주유소", "name": "동부에너지", "rating": 4.0, "road_node": "J08", "access_distance": 0.11},
    {"id": "P10", "category": "식당", "name": "초밥하루", "rating": 4.8, "road_node": "J09", "access_distance": 0.06},

    {"id": "P11", "category": "카페", "name": "브루잉랩", "rating": 4.8, "road_node": "J10", "access_distance": 0.13},
    {"id": "P12", "category": "주유소", "name": "빠른주유소", "rating": 4.4, "road_node": "J11", "access_distance": 0.10},
    {"id": "P13", "category": "식당", "name": "서가네국밥", "rating": 4.4, "road_node": "J12", "access_distance": 0.16},
    {"id": "P14", "category": "카페", "name": "서쪽다방", "rating": 4.1, "road_node": "J13", "access_distance": 0.08},
    {"id": "P15", "category": "주유소", "name": "서부셀프오일", "rating": 4.2, "road_node": "J14", "access_distance": 0.14},
    {"id": "P16", "category": "식당", "name": "왕돈까스", "rating": 4.0, "road_node": "J15", "access_distance": 0.09},
    {"id": "P17", "category": "카페", "name": "모카트리", "rating": 4.6, "road_node": "J16", "access_distance": 0.07},
    {"id": "P18", "category": "주유소", "name": "그린주유소", "rating": 4.7, "road_node": "J17", "access_distance": 0.12},
    {"id": "P19", "category": "식당", "name": "남쪽냉면", "rating": 4.5, "road_node": "J06", "access_distance": 0.18},
    {"id": "P20", "category": "카페", "name": "남쪽카페", "rating": 4.5, "road_node": "J05", "access_distance": 0.10},

    {"id": "P21", "category": "주유소", "name": "남부오일뱅크", "rating": 4.3, "road_node": "J07", "access_distance": 0.11},
    {"id": "P22", "category": "식당", "name": "한우정", "rating": 4.9, "road_node": "J08", "access_distance": 0.09},
    {"id": "P23", "category": "카페", "name": "크림라운지", "rating": 4.9, "road_node": "J09", "access_distance": 0.12},
    {"id": "P24", "category": "주유소", "name": "스마트주유소", "rating": 4.6, "road_node": "J10", "access_distance": 0.15},
    {"id": "P25", "category": "식당", "name": "마라공방", "rating": 4.3, "road_node": "J11", "access_distance": 0.08},
    {"id": "P26", "category": "카페", "name": "커피정원", "rating": 4.4, "road_node": "J12", "access_distance": 0.06},
    {"id": "P27", "category": "주유소", "name": "안심주유소", "rating": 3.9, "road_node": "J13", "access_distance": 0.13},
    {"id": "P28", "category": "식당", "name": "파스타온", "rating": 4.7, "road_node": "J14", "access_distance": 0.10},
    {"id": "P29", "category": "카페", "name": "카페봄", "rating": 4.0, "road_node": "J15", "access_distance": 0.05},
    {"id": "P30", "category": "주유소", "name": "하이웨이주유소", "rating": 4.8, "road_node": "J17", "access_distance": 0.09},
]


# ============================================================
# 2. 도로 노드 데이터
# 실제 네비게이션의 교차로, 도로 접속 지점 역할
# 장소 수 30개와 다르게 도로 노드는 18개만 사용
# ============================================================

ROAD_NODES = {
    "J00": "현재위치 인접 교차로",
    "J01": "시청앞사거리",
    "J02": "중앙시장입구",
    "J03": "북부교차로",
    "J04": "교육청앞",
    "J05": "남부광장",
    "J06": "터미널사거리",
    "J07": "동부시장입구",
    "J08": "산업단지입구",
    "J09": "호수공원앞",
    "J10": "테크노밸리입구",
    "J11": "대학로입구",
    "J12": "서부경찰서앞",
    "J13": "서부공원앞",
    "J14": "서부IC입구",
    "J15": "남서교차로",
    "J16": "문화센터앞",
    "J17": "고속도로진입로",
}


# ============================================================
# 3. 도로 데이터
# [도로명, from, to, 거리, 도로비]
# 거리 값은 기존 장소 샘플 거리와 반드시 같을 필요 없음
# toll_fee는 없으면 None
# ============================================================

ROAD_DATA = [
    {"road_name": "중앙대로", "from": "J00", "to": "J01", "distance": 0.6, "toll_fee": None},
    {"road_name": "중앙대로", "from": "J01", "to": "J02", "distance": 0.9, "toll_fee": None},
    {"road_name": "북부순환로", "from": "J02", "to": "J03", "distance": 1.4, "toll_fee": None},
    {"road_name": "교육청길", "from": "J02", "to": "J04", "distance": 1.1, "toll_fee": None},
    {"road_name": "남부로", "from": "J04", "to": "J05", "distance": 1.3, "toll_fee": None},
    {"road_name": "터미널로", "from": "J05", "to": "J06", "distance": 0.8, "toll_fee": None},

    {"road_name": "동부시장길", "from": "J01", "to": "J07", "distance": 1.2, "toll_fee": None},
    {"road_name": "산단로", "from": "J07", "to": "J08", "distance": 1.0, "toll_fee": None},
    {"road_name": "호수공원로", "from": "J08", "to": "J09", "distance": 1.5, "toll_fee": None},
    {"road_name": "테크노대로", "from": "J09", "to": "J10", "distance": 1.2, "toll_fee": None},
    {"road_name": "대학로", "from": "J10", "to": "J11", "distance": 1.1, "toll_fee": None},

    {"road_name": "서부대로", "from": "J04", "to": "J12", "distance": 1.6, "toll_fee": None},
    {"road_name": "공원길", "from": "J12", "to": "J13", "distance": 0.9, "toll_fee": None},
    {"road_name": "서부IC로", "from": "J13", "to": "J14", "distance": 1.4, "toll_fee": 800},
    {"road_name": "외곽순환고속화도로", "from": "J14", "to": "J17", "distance": 2.2, "toll_fee": 1200},

    {"road_name": "남서로", "from": "J13", "to": "J15", "distance": 1.0, "toll_fee": None},
    {"road_name": "문화센터길", "from": "J15", "to": "J16", "distance": 0.7, "toll_fee": None},
    {"road_name": "문화순환로", "from": "J16", "to": "J09", "distance": 1.6, "toll_fee": None},

    {"road_name": "강변로", "from": "J06", "to": "J10", "distance": 1.9, "toll_fee": None},
    {"road_name": "남부외곽로", "from": "J06", "to": "J15", "distance": 1.7, "toll_fee": None},

    {"road_name": "산단연결로", "from": "J08", "to": "J17", "distance": 2.0, "toll_fee": 700},
    {"road_name": "중앙터널", "from": "J03", "to": "J08", "distance": 1.8, "toll_fee": 500},
]
    
ROAD_GRAPH = {}

for node in ROAD_NODES:
    ROAD_GRAPH[node] = []

for road in ROAD_DATA:

    ROAD_GRAPH[road["from"]].append({
        "to": road["to"],
        "distance": road["distance"],
        "road_name": road["road_name"],
        "toll_fee": road["toll_fee"]
    })

    ROAD_GRAPH[road["to"]].append({
        "to": road["from"],
        "distance": road["distance"],
        "road_name": road["road_name"],
        "toll_fee": road["toll_fee"]
    })

# -------------------------------
# 예상 시간 계산
# -------------------------------
def calc_time(edge):

    speed = 50
    signal = 2

    driving = edge["distance"] / speed * 60
    return round(driving + signal, 1)

# -------------------------------
# Dijkstra 알고리즘
# -------------------------------
def dijkstra(start):

    distance = {}

    previous = {}

    for node in ROAD_GRAPH:
        distance[node] = float("inf")
        previous[node] = None

    distance[start] = 0

    pq = []

    heapq.heappush(pq,(0,start))

    while pq:

        current_cost,current = heapq.heappop(pq)

        if current_cost > distance[current]:
            continue

        for edge in ROAD_GRAPH[current]:

            nxt = edge["to"]

            cost = calc_time(edge)

            new_cost = current_cost + cost

            if new_cost < distance[nxt]:

                distance[nxt] = new_cost
                previous[nxt] = current

                heapq.heappush(
                    pq,
                    (new_cost,nxt)
                )

    return distance,previous

# -------------------------------
# 경로 복원
# -------------------------------
def build_path(previous,target):

    path=[]

    while target is not None:

        path.append(target)
        target=previous[target]

    path.reverse()

    return path

# -------------------------------
# 두 장소 사이 도로 찾기
# -------------------------------
def find_edge(frm,to):

    for edge in ROAD_GRAPH[frm]:

        if edge["to"]==to:
            return edge

    return None

# -------------------------------
# 경로 출력
# -------------------------------
def print_route(path, dist):

    print("\n========== 최단 경로 ==========\n")

    total_distance = 0

    for i, node in enumerate(path):

        print(f"{ROAD_NODES[node]} ({node})")

        if i != len(path)-1:

            edge = find_edge(node, path[i+1])

            total_distance += edge["distance"]

            print("  │")
            print(f"  ├─ 도로명 : {edge['road_name']}")
            print(f"  ├─ 거리 : {edge['distance']} km")
            print(f"  ├─ 통행료 : {edge['toll_fee']}")
            print(f"  └─ 예상시간 : {calc_time(edge)}분")
            print("  │")

    print("\n==============================")
    print(f"총 거리 : {round(total_distance,2)} km")
    print(f"예상 시간 : {round(dist,2)} 분")

# -------------------------------
# 장소 이름 검색
# -------------------------------
def search_name(keyword):

    result = []

    for node in POI_DATA:

        if keyword in node["name"]:
            result.append(node)

    return result


# -------------------------------
# 카테고리 검색
# -------------------------------
def search_category(category):

    result=[]

    for node in POI_DATA:

        if node["category"]==category:
            result.append(node)

    return result


# -------------------------------
# 평점 추천
# -------------------------------
def recommend(category):

    places = search_category(category)

    places.sort(
        key=lambda x:x["rating"],
        reverse=True
    )

    return places


# -------------------------------
# 모든 장소 출력
# -------------------------------
def print_all_places():

    print("\n========== 장소 목록 ==========\n")

    for node in POI_DATA:

        if node["id"]=="START":
            continue

        print(f"{node['id']:4} | {node['category']:5} | {node['name']:12} | ★ {node['rating']}")

    print()


# -------------------------------
# 길찾기
# -------------------------------
def navigation():

    print_all_places()

    target = input("\n목적지 ID 입력 : ").upper()

    poi = None

    for p in POI_DATA:
        if p["id"] == target:
            poi = p
            break

    if poi is None:
        print("없는 장소입니다.")
        return

    dist, prev = dijkstra("J00")

    target_node = poi["road_node"]

    path = build_path(prev, target_node)

    if dist[target_node] == float("inf"):
        print("경로가 없습니다.")
        return

    print_route(path, dist[target_node])

    print(f"\n목적지 : {poi['name']}")
    print(f"도보 이동 : {poi['access_distance']} km")


# -------------------------------
# 이름 검색
# -------------------------------
def name_search():

    keyword=input("검색어 : ")

    result=search_name(keyword)

    if len(result)==0:

        print("검색 결과가 없습니다.")
        return

    print()

    for node in result:

        print(
            f"{node['id']} | "
            f"{node['category']} | "
            f"{node['name']} | "
            f"★ {node['rating']}"
        )


# -------------------------------
# 카테고리 검색
# -------------------------------
def category_search():

    category=input("카테고리(식당/카페/주유소) : ")

    result=search_category(category)

    if len(result)==0:

        print("검색 결과가 없습니다.")
        return

    print()

    for node in result:

        print(
            f"{node['id']} | "
            f"{node['name']} | "
            f"★ {node['rating']}"
        )


# -------------------------------
# 평점 추천
# -------------------------------
def rating_recommend():

    category=input("카테고리(식당/카페/주유소) : ")

    result=recommend(category)

    if len(result)==0:

        print("검색 결과가 없습니다.")
        return

    print("\n평점순 추천\n")

    for i,node in enumerate(result,1):

        print(
            f"{i}. "
            f"{node['name']} "
            f"(★{node['rating']})"
        )


# -------------------------------
# 메인 메뉴
# -------------------------------
def menu():

    while True:

        print("""
===========================
        네비게이션
===========================

1. 장소 검색
2. 카테고리 검색
3. 평점 추천
4. 길찾기
5. 장소 목록
0. 종료

===========================
""")

        select=input("메뉴 선택 : ")

        if select=="1":

            name_search()

        elif select=="2":

            category_search()

        elif select=="3":

            rating_recommend()

        elif select=="4":

            navigation()

        elif select=="5":

            print_all_places()

        elif select=="0":

            print("프로그램을 종료합니다.")
            break

        else:

            print("잘못 입력했습니다.")


# -------------------------------
# 프로그램 시작
# -------------------------------

if __name__=="__main__":

    menu()