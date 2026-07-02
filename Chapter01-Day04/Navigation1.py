import heapq

# -------------------------------
# 샘플데이터
# -------------------------------
NAV_GRAPH = [
    {
        "id": "START",
        "category": "출발지",
        "name": "현재 위치",
        "rating": None,
        "edges": [
            {"to": "P03", "distance": 0.7},
            {"to": "P07", "distance": 1.2},
            {"to": "P15", "distance": 1.6},
            {"to": "P21", "distance": 1.1},
            {"to": "P25", "distance": 1.8},
        ]
    },

    {
        "id": "P01",
        "category": "식당",
        "name": "김치마을",
        "rating": 4.6,
        "edges": [
            {"to": "P03", "distance": 0.6},
            {"to": "P04", "distance": 0.9},
            {"to": "P18", "distance": 1.5},
        ]
    },
    {
        "id": "P02",
        "category": "주유소",
        "name": "북부셀프주유소",
        "rating": 4.1,
        "edges": [
            {"to": "P07", "distance": 0.7},
            {"to": "P30", "distance": 1.0},
        ]
    },
    {
        "id": "P03",
        "category": "카페",
        "name": "스타카페",
        "rating": 4.7,
        "edges": [
            {"to": "START", "distance": 0.7},
            {"to": "P01", "distance": 0.6},
            {"to": "P10", "distance": 1.4},
            {"to": "P12", "distance": 1.0},
        ]
    },
    {
        "id": "P04",
        "category": "식당",
        "name": "서울칼국수",
        "rating": 4.2,
        "edges": [
            {"to": "P01", "distance": 0.9},
            {"to": "P06", "distance": 0.8},
            {"to": "P14", "distance": 1.1},
        ]
    },
    {
        "id": "P05",
        "category": "카페",
        "name": "라떼하우스",
        "rating": 4.3,
        "edges": [
            {"to": "P10", "distance": 0.6},
            {"to": "P29", "distance": 1.5},
        ]
    },
    {
        "id": "P06",
        "category": "주유소",
        "name": "행복오일",
        "rating": 4.5,
        "edges": [
            {"to": "P04", "distance": 0.8},
            {"to": "P11", "distance": 1.2},
            {"to": "P20", "distance": 1.6},
        ]
    },
    {
        "id": "P07",
        "category": "식당",
        "name": "동쪽분식",
        "rating": 4.1,
        "edges": [
            {"to": "START", "distance": 1.2},
            {"to": "P02", "distance": 0.7},
            {"to": "P08", "distance": 0.5},
            {"to": "P13", "distance": 1.3},
        ]
    },
    {
        "id": "P08",
        "category": "카페",
        "name": "동쪽커피",
        "rating": 4.2,
        "edges": [
            {"to": "P07", "distance": 0.5},
            {"to": "P09", "distance": 0.9},
            {"to": "P17", "distance": 1.4},
        ]
    },
    {
        "id": "P09",
        "category": "주유소",
        "name": "동부에너지",
        "rating": 4.0,
        "edges": [
            {"to": "P08", "distance": 0.9},
            {"to": "P16", "distance": 0.8},
            {"to": "P23", "distance": 1.7},
        ]
    },
    {
        "id": "P10",
        "category": "식당",
        "name": "초밥하루",
        "rating": 4.8,
        "edges": [
            {"to": "P03", "distance": 1.4},
            {"to": "P05", "distance": 0.6},
            {"to": "P22", "distance": 1.9},
        ]
    },

    {
        "id": "P11",
        "category": "카페",
        "name": "브루잉랩",
        "rating": 4.8,
        "edges": [
            {"to": "P06", "distance": 1.2},
            {"to": "P28", "distance": 0.7},
        ]
    },
    {
        "id": "P12",
        "category": "주유소",
        "name": "빠른주유소",
        "rating": 4.4,
        "edges": [
            {"to": "P03", "distance": 1.0},
            {"to": "P19", "distance": 1.1},
            {"to": "P24", "distance": 1.5},
        ]
    },
    {
        "id": "P13",
        "category": "식당",
        "name": "서가네국밥",
        "rating": 4.4,
        "edges": [
            {"to": "P07", "distance": 1.3},
            {"to": "P15", "distance": 0.6},
            {"to": "P28", "distance": 1.0},
        ]
    },
    {
        "id": "P14",
        "category": "카페",
        "name": "서쪽다방",
        "rating": 4.1,
        "edges": [
            {"to": "P04", "distance": 1.1},
            {"to": "P26", "distance": 0.7},
        ]
    },
    {
        "id": "P15",
        "category": "주유소",
        "name": "서부셀프오일",
        "rating": 4.2,
        "edges": [
            {"to": "START", "distance": 1.6},
            {"to": "P13", "distance": 0.6},
            {"to": "P18", "distance": 0.9},
        ]
    },
    {
        "id": "P16",
        "category": "식당",
        "name": "왕돈까스",
        "rating": 4.0,
        "edges": [
            {"to": "P09", "distance": 0.8},
            {"to": "P27", "distance": 1.2},
        ]
    },
    {
        "id": "P17",
        "category": "카페",
        "name": "모카트리",
        "rating": 4.6,
        "edges": [
            {"to": "P08", "distance": 1.4},
            {"to": "P23", "distance": 0.9},
        ]
    },
    {
        "id": "P18",
        "category": "주유소",
        "name": "그린주유소",
        "rating": 4.7,
        "edges": [
            {"to": "P01", "distance": 1.5},
            {"to": "P15", "distance": 0.9},
            {"to": "P30", "distance": 1.4},
        ]
    },
    {
        "id": "P19",
        "category": "식당",
        "name": "남쪽냉면",
        "rating": 4.5,
        "edges": [
            {"to": "P12", "distance": 1.1},
            {"to": "P20", "distance": 0.5},
        ]
    },
    {
        "id": "P20",
        "category": "카페",
        "name": "남쪽카페",
        "rating": 4.5,
        "edges": [
            {"to": "P06", "distance": 1.6},
            {"to": "P19", "distance": 0.5},
            {"to": "P24", "distance": 0.8},
        ]
    },

    {
        "id": "P21",
        "category": "주유소",
        "name": "남부오일뱅크",
        "rating": 4.3,
        "edges": [
            {"to": "START", "distance": 1.1},
            {"to": "P22", "distance": 1.0},
            {"to": "P29", "distance": 0.7},
        ]
    },
    {
        "id": "P22",
        "category": "식당",
        "name": "한우정",
        "rating": 4.9,
        "edges": [
            {"to": "P10", "distance": 1.9},
            {"to": "P21", "distance": 1.0},
            {"to": "P23", "distance": 0.6},
        ]
    },
    {
        "id": "P23",
        "category": "카페",
        "name": "크림라운지",
        "rating": 4.9,
        "edges": [
            {"to": "P09", "distance": 1.7},
            {"to": "P17", "distance": 0.9},
            {"to": "P22", "distance": 0.6},
            {"to": "P30", "distance": 1.1},
        ]
    },
    {
        "id": "P24",
        "category": "주유소",
        "name": "스마트주유소",
        "rating": 4.6,
        "edges": [
            {"to": "P12", "distance": 1.5},
            {"to": "P20", "distance": 0.8},
            {"to": "P27", "distance": 1.3},
        ]
    },
    {
        "id": "P25",
        "category": "식당",
        "name": "마라공방",
        "rating": 4.3,
        "edges": [
            {"to": "START", "distance": 1.8},
            {"to": "P26", "distance": 0.4},
            {"to": "P28", "distance": 0.9},
        ]
    },
    {
        "id": "P26",
        "category": "카페",
        "name": "커피정원",
        "rating": 4.4,
        "edges": [
            {"to": "P14", "distance": 0.7},
            {"to": "P25", "distance": 0.4},
            {"to": "P29", "distance": 1.2},
        ]
    },
    {
        "id": "P27",
        "category": "주유소",
        "name": "안심주유소",
        "rating": 3.9,
        "edges": [
            {"to": "P16", "distance": 1.2},
            {"to": "P24", "distance": 1.3},
            {"to": "P30", "distance": 0.8},
        ]
    },
    {
        "id": "P28",
        "category": "식당",
        "name": "파스타온",
        "rating": 4.7,
        "edges": [
            {"to": "P11", "distance": 0.7},
            {"to": "P13", "distance": 1.0},
            {"to": "P25", "distance": 0.9},
        ]
    },
    {
        "id": "P29",
        "category": "카페",
        "name": "카페봄",
        "rating": 4.0,
        "edges": [
            {"to": "P05", "distance": 1.5},
            {"to": "P21", "distance": 0.7},
            {"to": "P26", "distance": 1.2},
        ]
    },
    {
        "id": "P30",
        "category": "주유소",
        "name": "하이웨이주유소",
        "rating": 4.8,
        "edges": [
            {"to": "P02", "distance": 1.0},
            {"to": "P18", "distance": 1.4},
            {"to": "P23", "distance": 1.1},
            {"to": "P27", "distance": 0.8},
        ]
    },
]

# -------------------------------
# 도로 정보
# -------------------------------

ROAD_INFO = {

    # ==========================================
    # 중앙대로
    # START → P03 → P10 → P22
    # ==========================================

    ("START","P03"):("중앙대로","왕복4차선",60,1.3),
    ("P03","START"):("중앙대로","왕복4차선",60,1.3),

    ("P03","P10"):("중앙대로","왕복4차선",60,1.3),
    ("P10","P03"):("중앙대로","왕복4차선",60,1.3),

    ("P10","P22"):("중앙대로","왕복4차선",60,1.3),
    ("P22","P10"):("중앙대로","왕복4차선",60,1.3),

    # ==========================================
    # 동부로
    # START → P07 → P08 → P09 → P16
    # ==========================================

    ("START","P07"):("동부로","왕복2차선",50,1.1),
    ("P07","START"):("동부로","왕복2차선",50,1.1),

    ("P07","P08"):("동부로","왕복2차선",50,1.1),
    ("P08","P07"):("동부로","왕복2차선",50,1.1),

    ("P08","P09"):("동부로","왕복2차선",50,1.1),
    ("P09","P08"):("동부로","왕복2차선",50,1.1),

    ("P09","P16"):("동부로","왕복2차선",50,1.1),
    ("P16","P09"):("동부로","왕복2차선",50,1.1),
    
    # ==========================================
    # 서부대로
    # START → P15 → P13 → P28 → P11
    # ==========================================

    ("START","P15"):("서부대로","왕복4차선",60,1.0),
    ("P15","START"):("서부대로","왕복4차선",60,1.0),

    ("P15","P13"):("서부대로","왕복4차선",60,1.0),
    ("P13","P15"):("서부대로","왕복4차선",60,1.0),

    ("P13","P28"):("서부대로","왕복4차선",60,1.0),
    ("P28","P13"):("서부대로","왕복4차선",60,1.0),

    ("P28","P11"):("서부대로","왕복4차선",60,1.0),
    ("P11","P28"):("서부대로","왕복4차선",60,1.0),

    # ==========================================
    # 북부로
    # P01 → P04 → P06
    # ==========================================

    ("P01","P04"):("북부로","왕복2차선",50,1.1),
    ("P04","P01"):("북부로","왕복2차선",50,1.1),

    ("P04","P06"):("북부로","왕복2차선",50,1.1),
    ("P06","P04"):("북부로","왕복2차선",50,1.1),

    # 북부 연결도로

    ("P01","P03"):("시장로","일반도로",40,1.2),
    ("P03","P01"):("시장로","일반도로",40,1.2),

    ("P01","P18"):("북부연결로","왕복4차선",60,1.0),
    ("P18","P01"):("북부연결로","왕복4차선",60,1.0),

    ("P06","P11"):("산업로","왕복2차선",50,1.1),
    ("P11","P06"):("산업로","왕복2차선",50,1.1),

    ("P06","P20"):("산업로","왕복2차선",50,1.1),
    ("P20","P06"):("산업로","왕복2차선",50,1.1),

    ("P04","P14"):("북공원길","일반도로",40,1.2),
    ("P14","P04"):("북공원길","일반도로",40,1.2),
    
    # ==========================================
    # 남부대로
    # START → P21 → P29 → P26 → P25
    # ==========================================

    ("START","P21"):("남부대로","왕복4차선",60,1.2),
    ("P21","START"):("남부대로","왕복4차선",60,1.2),

    ("P21","P29"):("남부대로","왕복4차선",60,1.2),
    ("P29","P21"):("남부대로","왕복4차선",60,1.2),

    ("P29","P26"):("남부대로","왕복4차선",60,1.2),
    ("P26","P29"):("남부대로","왕복4차선",60,1.2),

    ("P26","P25"):("남부대로","왕복4차선",60,1.2),
    ("P25","P26"):("남부대로","왕복4차선",60,1.20),

    # ==========================================
    # 강변로
    # P03 → P12 → P19 → P20 → P24
    # ==========================================

    ("P03","P12"):("강변로","왕복2차선",50,1.0),
    ("P12","P03"):("강변로","왕복2차선",50,1.0),

    ("P12","P19"):("강변로","왕복2차선",50,1.0),
    ("P19","P12"):("강변로","왕복2차선",50,1.0),

    ("P19","P20"):("강변로","왕복2차선",50,1.0),
    ("P20","P19"):("강변로","왕복2차선",50,1.0),

    ("P20","P24"):("강변로","왕복2차선",50,1.0),
    ("P24","P20"):("강변로","왕복2차선",50,1.0),

    # ==========================================
    # 공원로
    # P13 ↔ P28, P14 ↔ P26, P25 ↔ P26
    # ==========================================

    ("P28","P13"):("공원로","일반도로",40,1.1),
    ("P13","P28"):("공원로","일반도로",40,1.1),

    ("P26","P14"):("공원로","일반도로",40,1.1),
    ("P14","P26"):("공원로","일반도로",40,1.1),
    
    ("P25","P26"):("공원로","일반도로",40,1.1),
    ("P26","P25"):("공원로","일반도로",40,1.1),

    # ==========================================
    # 동부순환로
    # P24 → P27 → P30 → (IC)
    # ===========================================
    
    ("P24","P27"):("동부순환로","고속화도로",80,0.8),
    ("P27","P24"):("동부순환로","고속화도로",80,0.8),

    ("P27","P30"):("동부순환로","고속화도로",80,0.8),
    ("P30","P27"):("동부순환로","고속화도로",80,0.8),

    # ==========================================
    # 연결도로
    # ==========================================

    ("P02","P07"):("동부IC연결로","일반도로",40,1.2),
    ("P07","P02"):("동부IC연결로","일반도로",40,1.2),

    ("P02","P30"):("동부IC진입로","고속화도로",70,0.9),
    ("P30","P02"):("동부IC진입로","고속화도로",70,0.9),

    ("P22","P23"):("공항로","고속화도로",80,0.9),
    ("P23","P22"):("공항로","고속화도로",80,0.9),

    ("P05","P10"):("맛집거리","일반도로",30,1.3),
    ("P10","P05"):("맛집거리","일반도로",30,1.3),

    ("P05","P29"):("남부연결로","왕복2차선",50,1.1),
    ("P29","P05"):("남부연결로","왕복2차선",50,1.1),

    ("P08","P17"):("카페거리","일반도로",30,1.3),
    ("P17","P08"):("카페거리","일반도로",30,1.3),

    ("P09","P23"):("동부간선로","왕복4차선",60,1.0),
    ("P23","P09"):("동부간선로","왕복4차선",60,1.0),

    ("P15","P18"):("서부연결로","왕복2차선",50,1.1),
    ("P18","P15"):("서부연결로","왕복2차선",50,1.1),

    ("P16","P27"):("동부산업로","왕복2차선",50,1.1),
    ("P27","P16"):("동부산업로","왕복2차선",50,1.1),

    ("P17","P23"):("호수로","왕복2차선",50,1.1),
    ("P23","P17"):("호수로","왕복2차선",50,1.1),

    ("P18","P30"):("동부연결로","왕복4차선",60,1.0),
    ("P30","P18"):("동부연결로","왕복4차선",60,1.0),

    ("P21","P22"):("한우대로","왕복4차선",60,1.2),
    ("P22","P21"):("한우대로","왕복4차선",60,1.2),

    ("P23","P30"):("공항로","고속화도로",80,0.9),
    ("P30","P23"):("공항로","고속화도로",80,0.9),

}
    
ROAD_GRAPH = {}
PLACE_INFO = {}

for node in NAV_GRAPH:

    PLACE_INFO[node["id"]] = node
    ROAD_GRAPH[node["id"]] = []

    for edge in node["edges"]:

        info = ROAD_INFO.get(
            (node["id"], edge["to"]),
            ("이면도로", "일반도로", 40, 1.2)
        )

        ROAD_GRAPH[node["id"]].append({

            "to": edge["to"],
            "distance": edge["distance"],
            "road_name": info[0],
            "road_type": info[1],
            "speed": info[2],
            "traffic": info[3]

        })

# -------------------------------
# 예상 시간 계산
# -------------------------------
def calc_time(edge):

    driving = edge["distance"] / edge["speed"] * 60

    signal = 3

    return round((driving + signal) * edge["traffic"],1)

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
def print_route(path,dist):

    print("\n========== 최단 경로 ==========\n")

    total_distance = 0

    for i,node in enumerate(path):

        info = PLACE_INFO[node]

        print(f"{info['name']} ({node})")

        if i != len(path)-1:

            edge = find_edge(node,path[i+1])

            total_distance += edge["distance"]

            print(f"  │")
            print(f"  ├─ {edge['road_name']}")
            print(f"  ├─ {edge['road_type']}")
            print(f"  ├─ 제한속도 : {edge['speed']}km/h")
            print(f"  ├─ 거리 : {edge['distance']}km")
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

    for node in NAV_GRAPH:

        if keyword in node["name"]:
            result.append(node)

    return result


# -------------------------------
# 카테고리 검색
# -------------------------------
def search_category(category):

    result=[]

    for node in NAV_GRAPH:

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

    for node in NAV_GRAPH:

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

    if target not in PLACE_INFO:

        print("없는 장소입니다.")
        return

    dist, prev = dijkstra("START")

    path = build_path(prev,target)

    if dist[target]==float("inf"):

        print("경로가 없습니다.")
        return

    print_route(path,dist[target])


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