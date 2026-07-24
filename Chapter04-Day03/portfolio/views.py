import os
from copy import deepcopy
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render


def _contact_email():
    value = os.environ.get("PORTFOLIO_CONTACT_EMAIL", "").strip()
    if not value:
        return ""
    try:
        validate_email(value)
    except ValidationError:
        return ""
    return value


def _social_link(name, prefix):
    handle = os.environ.get(f"PORTFOLIO_{prefix}_HANDLE", "").strip()
    url = os.environ.get(f"PORTFOLIO_{prefix}_URL", "").strip()
    parsed = urlsplit(url)
    if not handle or parsed.scheme != "https" or not parsed.netloc:
        return None
    return {"name": name, "handle": handle, "url": url}


PROFILE = {
    "name": "최원준",
    "english_name": "Choi WonJun",
    "role": "동아대학교 컴퓨터공학과 1학년",
    "email": _contact_email(),
    "github": "https://github.com/lWonJunl",
    "intro": "알고리즘과 데이터를 바탕으로 풀스택 웹 서비스와 인공지능을 직접 구현하고 탐구합니다.",
    "about": (
        "동아대학교 컴퓨터공학과 1학년으로 Python, C/C++와 알고리즘의 기반을 다지고 있습니다. "
        "공공데이터와 과학·ICT 융합 탐구에서 출발해 Django 기반 웹 서비스, 데이터 분석과 인공지능으로 관심을 확장하고 있습니다. "
        "배운 원리를 직접 구현하고 Linux 서버에서 실행해 본 과정을 GitHub에 기록합니다."
    ),
}

SOCIAL_LINKS = [
    link
    for link in (
        _social_link("Instagram", "INSTAGRAM"),
        _social_link("Naver Blog", "NAVER_BLOG"),
        _social_link("Kakao Open Chat", "KAKAO_OPEN_CHAT"),
    )
    if link is not None
]

STATS = [
    {"value": "22", "label": "Projects & research"},
    {"value": "05", "label": "Code archives"},
    {"value": "100+", "label": "Practice solutions"},
]

SKILLS = [
    {"name": "Python", "level": 78},
    {"name": "Algorithms", "level": 68},
    {"name": "Data Analysis", "level": 64},
    {"name": "Django & Web", "level": 56},
    {"name": "SQL", "level": 52},
    {"name": "C / C++", "level": 25},
]

PROJECTS = [
    {
        "number": "01",
        "title": "동아대학교 캠퍼스 길찾기",
        "description": "155개 장소와 171개 도로 데이터를 바탕으로 다익스트라 최단 경로를 계산하고 카카오 지도에 시각화한 웹 서비스입니다.",
        "tags": ["Python", "Dijkstra", "SQL", "Kakao Maps"],
        "link": "https://github.com/MSILJI0708/dongamap",
        "color": "coral",
    },
    {
        "number": "02",
        "title": "엘니뇨·라니냐와 태풍 분석",
        "description": "1990년부터 2023년까지의 기상청 태풍 데이터를 전처리하고 해수면 온도 현상과 태풍 강도의 관계를 탐구했습니다.",
        "tags": ["Python", "Pandas", "Data Visualization"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/엘니뇨%20라니냐와%20태풍의%20관계%20데이터%20분석%20프로젝트/README.md",
        "color": "lime",
    },
    {
        "number": "03",
        "title": "상대성이론과 GNSS 오차 분석",
        "description": "Python으로 특수·일반상대성이론의 시간 지연을 계산하고, 하루 약 38μs의 차이를 보정하지 않으면 GNSS 위치가 약 11.4km 어긋날 수 있음을 시스템 정확도 관점에서 분석했습니다.",
        "tags": ["Python", "GNSS", "Error Correction", "ICT"],
        "link": "",
        "color": "violet",
    },
    {
        "number": "04",
        "title": "Pygame 벽돌깨기",
        "description": "객체의 이동과 충돌 판정, 점수와 게임 상태를 직접 다루며 완성한 Python Programming 과목의 최종 게임 프로젝트입니다.",
        "tags": ["Python", "Pygame", "Game Logic"],
        "link": "https://github.com/lWonJunl/donga-univ-cse/blob/main/1-1/Python_Programming/Week%2014/README.md",
        "color": "blue",
    },
]

PROJECT_ARCHIVE = [
    {
        "year": "2024.07.12",
        "category": "AI Optimization",
        "title": "경사하강법과 SDGs 정책 방향 탐구",
        "description": "AI 모델의 손실을 줄이는 최적화 과정에 주목해 평균제곱오차, 가중치, 학습률과 지역 최솟값의 관계를 정리하고 정책 데이터 예측에 적용할 가능성을 탐구한 소논문입니다.",
        "tags": ["Gradient Descent", "Loss Function", "AI", "SDGs"],
        "link": "",
    },
    {
        "year": "2024.11",
        "category": "Emerging Computing",
        "title": "DNA 컴퓨팅과 데이터 저장",
        "description": "이진 정보를 DNA 염기서열로 인코딩하는 방식과 분자 단위 병렬 계산·고밀도 저장 원리를 조사하고 입출력 속도, 검색과 비용 측면의 기술적 한계를 분석한 소논문입니다.",
        "tags": ["DNA Computing", "Encoding", "Parallelism", "Storage"],
        "link": "",
    },
    {
        "year": "2023",
        "category": "Machine Learning",
        "title": "최저임금과 물가 예측",
        "description": "KOSIS 물가 데이터와 연도별 최저임금 자료를 결합해 두 지표의 관계를 분석하고 물가 상승 흐름을 예측했습니다.",
        "tags": ["Python", "Regression", "Public Data"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/최저임금에%20따른%20물가%20상승률%20예측%20모델%20제작%20프로젝트/README.md",
    },
    {
        "year": "2026",
        "category": "Web",
        "title": "Django 개인 포트폴리오",
        "description": "Django 템플릿과 반응형 CSS, Vanilla JavaScript로 제작한 현재의 포트폴리오 웹사이트입니다.",
        "tags": ["Django", "HTML", "CSS", "JavaScript"],
        "link": "",
    },
    {
        "year": "2026",
        "category": "Data",
        "title": "Google News RSS 추천기",
        "description": "Feedparser로 뉴스 RSS를 읽고 관심 키워드를 기준으로 관련 기사를 정리하는 Python 미니 프로젝트입니다.",
        "tags": ["Python", "Feedparser", "RSS"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp/blob/main/Chapter01-Day02/README_Google_News_RSS.md",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "이미지 기반 미로 탐색",
        "description": "OpenCV로 미로 이미지를 이진화하고 NumPy와 BFS를 이용해 이동 가능한 경로를 탐색했습니다.",
        "tags": ["OpenCV", "NumPy", "BFS"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp/blob/main/Chapter01-Day04/README_Image_Maze_Solver.md",
    },
    {
        "year": "2023",
        "category": "Machine Learning",
        "title": "2030년 서울 기온 예측",
        "description": "장기간 서울 기온 데이터를 정리하고 회귀 모델을 학습해 미래 평균기온을 예측했습니다.",
        "tags": ["Pandas", "Regression", "Matplotlib"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/AI%20club%20for%20learning%20through%20projects/README_2030_Temperature.md",
    },
    {
        "year": "2023",
        "category": "Machine Learning",
        "title": "공공자전거 수요 예측",
        "description": "공공자전거 데이터를 훈련·평가 데이터로 나누고 수요를 예측하는 머신러닝 과정을 실습했습니다.",
        "tags": ["Scikit-learn", "Pandas", "Prediction"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/AI%20club%20for%20learning%20through%20projects/README_Public_Bike_Demand.md",
    },
    {
        "year": "2023",
        "category": "Data",
        "title": "월별 불쾌지수 분석",
        "description": "기상개황 자료를 가공해 월별 불쾌지수의 변화를 계산하고 그래프로 비교했습니다.",
        "tags": ["Pandas", "Matplotlib", "Weather Data"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/2023%20information%20subject/README_Discomfort_Index.md",
    },
    {
        "year": "2023",
        "category": "Data",
        "title": "인구 데이터 시각화",
        "description": "연령별 인구 데이터를 NumPy와 Pandas로 가공하고 분포를 시각적으로 표현했습니다.",
        "tags": ["NumPy", "Pandas", "Visualization"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/AI%20club%20for%20learning%20through%20projects/README_Population_Visualization.md",
    },
    {
        "year": "2023",
        "category": "Data",
        "title": "기상 공공데이터 처리",
        "description": "공공 기상 자료를 불러와 필요한 열을 선택하고 정제·집계·시각화하는 분석 흐름을 실습했습니다.",
        "tags": ["Public Data", "Pandas", "Jupyter"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool/blob/main/AI%20club%20for%20learning%20through%20projects/README_Weather_Public_Data.md",
    },
    {
        "year": "2023",
        "category": "Python GUI",
        "title": "원자 모형 시뮬레이터",
        "description": "원소를 선택하면 원자 번호에 맞는 전자 배치를 계산해 Turtle 애니메이션으로 표현했습니다.",
        "tags": ["Python", "Turtle", "PySimpleGUI"],
        "link": "https://github.com/lWonJunl/bgcec-22nd/blob/main/Python_Programming/README_Atomic_Model.md",
    },
    {
        "year": "2023",
        "category": "Geometry",
        "title": "충돌 없는 랜덤 원 배치",
        "description": "원의 중심 거리와 반지름을 비교해 서로 겹치지 않는 원을 무작위로 배치했습니다.",
        "tags": ["Python", "Geometry", "Random"],
        "link": "https://github.com/lWonJunl/bgcec-22nd/blob/main/Python_Programming/README_Random_Circle.md",
    },
    {
        "year": "2023",
        "category": "Geometry",
        "title": "충돌 없는 랜덤 사각형 배치",
        "description": "사각형의 좌표와 너비·높이를 이용해 충돌 여부를 검사하고 겹치지 않도록 생성했습니다.",
        "tags": ["Python", "Geometry", "Collision"],
        "link": "https://github.com/lWonJunl/bgcec-22nd/blob/main/Python_Programming/README_Random_Rectangle.md",
    },
    {
        "year": "2023",
        "category": "Python GUI",
        "title": "Turtle 드로잉 컨트롤",
        "description": "키보드와 마우스 이벤트로 Turtle을 움직이고 화면을 지우며 자유롭게 그림을 그리도록 구현했습니다.",
        "tags": ["Python", "Turtle", "Event Handling"],
        "link": "https://github.com/lWonJunl/bgcec-22nd",
    },
    {
        "year": "2023",
        "category": "Algorithm",
        "title": "유클리드 최대공약수 계산기",
        "description": "두 정수에 유클리드 호제법을 반복 적용해 최대공약수를 계산하는 수론 프로그램입니다.",
        "tags": ["Python", "Euclidean Algorithm", "GCD"],
        "link": "https://github.com/lWonJunl/bgcec-22nd",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "금액 조합 경우의 수 계산",
        "description": "여러 화폐 단위로 목표 금액을 만드는 경우의 수를 동적 계획법의 Tabulation 방식으로 계산했습니다.",
        "tags": ["Python", "Dynamic Programming", "Tabulation"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "재귀 피보나치 수열",
        "description": "점화식을 재귀 호출로 구현하며 중복 연산이 발생하는 기본 피보나치 계산 방식을 확인했습니다.",
        "tags": ["Python", "Recursion", "Fibonacci"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "메모이제이션 피보나치 수열",
        "description": "이미 계산한 값을 저장해 재귀 피보나치의 중복 연산을 줄이는 Top-down 방식을 구현했습니다.",
        "tags": ["Python", "Memoization", "Fibonacci"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "테이블 피보나치 수열",
        "description": "작은 항부터 결과를 배열에 저장하며 답을 구하는 Bottom-up 동적 계획법을 구현했습니다.",
        "tags": ["Python", "Tabulation", "Fibonacci"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "두 칸 계단 오르기",
        "description": "한 번에 1칸 또는 2칸을 오를 때 가능한 이동 방법의 수를 동적 계획법으로 계산했습니다.",
        "tags": ["Python", "Dynamic Programming", "Stairs"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "세 칸 계단 오르기",
        "description": "1칸부터 3칸까지 이동할 수 있는 계단 문제의 점화식을 세우고 배열로 계산했습니다.",
        "tags": ["Python", "Dynamic Programming", "Stairs"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "그리디 동전 거스름돈",
        "description": "큰 단위의 동전부터 선택하는 그리디 전략으로 거스름돈에 필요한 동전 수를 계산했습니다.",
        "tags": ["Python", "Greedy", "Coin Change"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "회의실 일정 선택",
        "description": "종료 시간이 빠른 회의부터 선택해 서로 겹치지 않는 최대 회의 일정을 구했습니다.",
        "tags": ["Python", "Greedy", "Scheduling"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "너비 우선 탐색 구현",
        "description": "큐를 사용해 그래프의 가까운 정점부터 방문하는 BFS 탐색 순서를 구현했습니다.",
        "tags": ["Python", "BFS", "Queue", "Graph"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "깊이 우선 탐색 구현",
        "description": "한 경로를 끝까지 탐색한 뒤 되돌아오는 DFS의 방문 과정을 그래프로 구현했습니다.",
        "tags": ["Python", "DFS", "Stack", "Graph"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "다익스트라 최단 경로 구현",
        "description": "우선순위 큐로 가중 그래프의 최단 거리와 이전 정점을 계산하고 실제 이동 경로를 복원했습니다.",
        "tags": ["Python", "Dijkstra", "Heap", "Graph"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp",
    },
    {
        "year": "2026",
        "category": "Algorithm",
        "title": "IDA* 루빅스 큐브 풀이",
        "description": "3×3 큐브의 면 회전을 배열로 모델링하고 휴리스틱과 반복 깊이 탐색을 이용해 섞인 상태의 해법을 찾았습니다.",
        "tags": ["Python", "IDA*", "Heuristic Search", "Simulation"],
        "link": "https://github.com/lWonJunl/2026-donga-ai-sw-summer-bootcamp/blob/main/Chapter01-Day03/README_IDA_Star_Rubiks_Cube.md",
    },
    {
        "year": "2023",
        "category": "Python",
        "title": "내신 등급 계산 프로그램",
        "description": "과목별 점수를 입력받아 조건에 따라 성적 등급을 계산하는 콘솔 프로그램을 제작했습니다.",
        "tags": ["Python", "Conditional", "Console"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Python",
        "title": "가위바위보 프로그램",
        "description": "사용자와 컴퓨터의 선택을 비교해 승패를 판정하는 조건문 기반 게임을 구현했습니다.",
        "tags": ["Python", "Random", "Game Logic"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Python",
        "title": "숫자 맞히기 게임",
        "description": "무작위 정답과 사용자의 입력을 비교하고 힌트를 제공하는 반복문 기반 게임을 만들었습니다.",
        "tags": ["Python", "Random", "Loop"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Python",
        "title": "지폐 개수 계산기",
        "description": "입력 금액을 화폐 단위별 몫과 나머지로 나누어 필요한 지폐 수를 계산했습니다.",
        "tags": ["Python", "Arithmetic", "Console"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Python",
        "title": "영화 예매 프로그램",
        "description": "관람 정보와 수량을 입력받아 예매 내용과 금액을 처리하는 콘솔 프로그램을 구현했습니다.",
        "tags": ["Python", "Input", "Control Flow"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Algorithm",
        "title": "3중 반복문 조합 생성",
        "description": "중첩 반복문으로 여러 값의 가능한 조합을 생성하며 탐색 구조와 반복 흐름을 실습했습니다.",
        "tags": ["Python", "Nested Loop", "Combination"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Python GUI",
        "title": "미키마우스 Turtle 드로잉",
        "description": "좌표와 원호를 조합해 미키마우스 형태를 그리는 Turtle 그래픽 프로그램을 제작했습니다.",
        "tags": ["Python", "Turtle", "Drawing"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "2023",
        "category": "Python GUI",
        "title": "꽃 패턴 Turtle 드로잉",
        "description": "반복되는 회전과 이동 명령을 조합해 꽃 형태의 기하 패턴을 그렸습니다.",
        "tags": ["Python", "Turtle", "Pattern"],
        "link": "https://github.com/lWonJunl/busanjungang-highschool",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "버튼으로 텍스트 변경",
        "description": "버튼 클릭 이벤트에서 DOM 요소를 찾아 화면의 텍스트를 변경했습니다.",
        "tags": ["HTML", "JavaScript", "DOM"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "매개변수 기반 텍스트 전환",
        "description": "두 버튼에서 서로 다른 값을 함수 매개변수로 전달해 하나의 텍스트 요소를 전환했습니다.",
        "tags": ["HTML", "JavaScript", "Function"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "ON/OFF 상태 토글",
        "description": "변수와 조건문을 사용해 버튼을 누를 때마다 ON과 OFF 상태가 바뀌도록 구현했습니다.",
        "tags": ["JavaScript", "State", "Conditional"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "증감 카운터",
        "description": "상태 값을 저장하고 증가·감소 버튼 이벤트에 따라 화면의 숫자를 갱신했습니다.",
        "tags": ["JavaScript", "DOM", "Counter"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "입력값 검증 UI",
        "description": "사용자 입력이 비어 있는지와 숫자·문자 여부를 검사해 서로 다른 결과를 표시했습니다.",
        "tags": ["JavaScript", "Validation", "Input"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "DOM 색상·표시 제어",
        "description": "버튼 이벤트로 요소의 글자색과 표시 상태를 직접 변경하며 DOM 스타일 제어를 구현했습니다.",
        "tags": ["JavaScript", "DOM", "CSS"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Frontend",
        "title": "CSS 기본 레이아웃",
        "description": "선택자, 여백, 테두리와 크기 속성을 적용해 웹 페이지의 기본 레이아웃을 구성했습니다.",
        "tags": ["HTML", "CSS", "Layout"],
        "link": "https://github.com/lWonJunl/my-study",
    },
    {
        "year": "Study",
        "category": "Problem Solving",
        "title": "C·Python 문제 풀이 아카이브",
        "description": "CodeUp과 백준 문제를 풀며 입출력, 자료형, 조건문, 반복문, 문자열과 배열의 기초를 다졌습니다.",
        "tags": ["C", "Python", "BOJ", "CodeUp"],
        "link": "https://github.com/lWonJunl/my-study",
    },
]

CURATED_PROJECT_TITLES = {
    "경사하강법과 SDGs 정책 방향 탐구",
    "DNA 컴퓨팅과 데이터 저장",
    "최저임금과 물가 예측",
    "Django 개인 포트폴리오",
    "Google News RSS 추천기",
    "이미지 기반 미로 탐색",
    "2030년 서울 기온 예측",
    "공공자전거 수요 예측",
    "월별 불쾌지수 분석",
    "인구 데이터 시각화",
    "기상 공공데이터 처리",
    "원자 모형 시뮬레이터",
    "충돌 없는 랜덤 원 배치",
    "충돌 없는 랜덤 사각형 배치",
    "IDA* 루빅스 큐브 풀이",
}

PROJECT_ARCHIVE = [
    project
    for project in PROJECT_ARCHIVE
    if project["title"] in CURATED_PROJECT_TITLES
]

STATS[0]["value"] = str(len(PROJECTS) + len(PROJECT_ARCHIVE))

ARCHIVE_FILTER_GROUPS = {
    "AI Optimization": "연구",
    "Emerging Computing": "연구",
    "Machine Learning": "AI · 데이터",
    "Data": "AI · 데이터",
    "Web": "웹",
    "Frontend": "웹",
    "Algorithm": "알고리즘",
    "Geometry": "알고리즘",
    "Problem Solving": "알고리즘",
    "Python GUI": "Python",
    "Python": "Python",
}

for project in PROJECT_ARCHIVE:
    project["filter_group"] = ARCHIVE_FILTER_GROUPS[project["category"]]

ARCHIVE_FILTERS = list(
    dict.fromkeys(project["filter_group"] for project in PROJECT_ARCHIVE)
)

LEARNING_AREAS = [
    {
        "number": "01",
        "title": "Algorithm & Problem Solving",
        "description": "동적 계획법, 그리디, BFS·DFS, 다익스트라부터 CodeUp과 백준 풀이까지 문제 해결 과정을 코드로 기록했습니다.",
        "keywords": "DP · GREEDY · GRAPH · BOJ",
    },
    {
        "number": "02",
        "title": "Data, AI & Science",
        "description": "공공데이터 분석과 머신러닝부터 경사하강법, DNA 컴퓨팅, 상대성이론과 GNSS까지 과학적 원리를 컴퓨팅 관점에서 탐구했습니다.",
        "keywords": "PANDAS · SCIKIT-LEARN · PHYSICS · ICT",
    },
    {
        "number": "03",
        "title": "Web & Backend",
        "description": "HTML·CSS·JavaScript의 DOM부터 Django, MySQL, Linux 서버와 지도 API 연결까지 익히며 풀스택 구조를 학습하고 있습니다.",
        "keywords": "DJANGO · MYSQL · JAVASCRIPT · LINUX",
    },
    {
        "number": "04",
        "title": "Programming Foundations",
        "description": "C/C++와 Python의 기초, 객체지향, 파일 입출력, Tkinter·Turtle·Pygame GUI 프로그램을 꾸준히 실습했습니다.",
        "keywords": "C/C++ · OOP · GUI · FILE I/O",
    },
]

JOURNEY = [
    {
        "period": "2023",
        "title": "2023년 부산광역시정보영재교육원 고1정보심화반",
        "organization": "부산광역시정보영재교육원 · 차석 수료",
        "award": "교육감상",
        "award_detail": "(성적우수 / 2위)",
        "award_rank": 2,
        "description": "Python 프로그래밍, 수학 기반 알고리즘과 인공지능 이론을 학습하고 프로젝트를 수행하며 컴퓨터공학에 대한 관심을 구체화했습니다.",
    },
    {
        "period": "2023",
        "title": "정보 교과에서 데이터 다루기",
        "organization": "부산중앙고등학교 · 정보 교과",
        "award": "교과우수상",
        "award_detail": "(전교1등)",
        "award_rank": 1,
        "description": "Python 기초 문법을 익히고 기상개황 자료의 월별 불쾌지수와 연령별 인구 데이터를 가공·시각화했습니다.",
    },
    {
        "period": "2023",
        "title": "AI 프로젝트로 예측 경험 쌓기",
        "organization": "부산중앙고등학교 · AI 프로젝트 동아리",
        "description": "기상과 공공자전거 데이터를 분석하고 2030년 기온과 자전거 수요를 예측하며 머신러닝의 데이터 분리·학습·평가 과정을 경험했습니다.",
    },
    {
        "period": "2024.07.12",
        "title": "경사하강법과 SDGs 정책 방향 탐구",
        "organization": "부산중앙고등학교 · 창의융합주간 주제탐구 소논문",
        "description": "AI 모델의 손실함수를 최소화하는 경사하강법의 원리와 학습률에 따른 한계를 살펴보고 정책 데이터 예측에 적용할 가능성을 탐구했습니다.",
    },
    {
        "period": "2024.11",
        "title": "DNA 컴퓨팅과 데이터 저장",
        "organization": "부산중앙고등학교 · 생활과 과학 주제탐구 소논문",
        "description": "DNA 염기서열을 이용한 정보 인코딩, 병렬 계산과 고밀도 저장 원리를 조사하고 입출력 속도·검색·비용 등 컴퓨팅 시스템으로서의 과제를 정리했습니다.",
    },
    {
        "period": "2025.03 — 06",
        "title": "상대성이론이 만드는 위치 정확도",
        "organization": "부산중앙고등학교 · 과학과제연구 소논문",
        "description": "Python으로 GNSS 위성의 상대론적 시간 지연을 계산하고 작은 시간 오차를 보정하는 과정이 위치 기반 정보통신 시스템의 정확도를 결정하는 이유를 분석했습니다.",
    },
    {
        "period": "2026.03 — 현재",
        "title": "컴퓨터공학의 기반 다지기",
        "organization": "동아대학교 컴퓨터공학과 · 재학",
        "description": "전공 수업과 학회 스터디에서 Python, C/C++의 기초 문법과 객체지향, 문제 해결 방법을 계속 배우고 있습니다.",
    },
    {
        "period": "2026.05 — 06",
        "title": "2026 기상 빅데이터 콘테스트 참가",
        "organization": "한국기상청 주최 · 참가",
        "description": "기상 빅데이터에서 해결할 문제를 정의하고 분석 아이디어를 프로젝트 형태로 구체화하는 과정을 경험했습니다.",
    },
    {
        "period": "2026.06.29 — 07.08",
        "title": "2026 NYPC 대회 참가",
        "organization": "넥슨 주최 · 참가",
        "description": "대회 기간 동안 제한 시간 안에 문제의 조건을 분석하고 Python으로 풀이를 구현·검증하는 경험을 쌓았습니다.",
    },
    {
        "period": "2026.06.29 — 08.21",
        "title": "2026 동아 AI·SW 여름 부트캠프",
        "organization": "동아대학교 소프트웨어중심대학",
        "description": "알고리즘, MySQL, 프런트엔드와 Django를 학습하며 캠퍼스 길찾기 서비스와 개인 포트폴리오를 구현하고 있습니다.",
    },
]


PROFILE_EN = {
    "display_name": "Choi WonJun",
    "role": "First-year Computer Engineering Student at Dong-A University",
    "intro": "I build and explore full-stack web services and AI applications on a foundation of algorithms and data.",
    "about": (
        "I am a first-year Computer Engineering student at Dong-A University, building a foundation in Python, C/C++, and algorithms. "
        "Starting from public-data analysis and interdisciplinary science-ICT research, "
        "I am expanding into Django web services, data analysis, and AI. I document what I learn by implementing it, running it on Linux, and sharing the process on GitHub."
    ),
}

PROJECT_TRANSLATIONS = {
    "동아대학교 캠퍼스 길찾기": {
        "title": "Dong-A University Campus Navigator",
        "description": "A web service that computes Dijkstra shortest paths across 155 campus locations and 171 road segments, then visualizes the route with Kakao Maps.",
    },
    "엘니뇨·라니냐와 태풍 분석": {
        "title": "El Niño, La Niña & Typhoon Analysis",
        "description": "I cleaned Korea Meteorological Administration typhoon data from 1990–2023 and examined how sea-surface temperature patterns relate to typhoon intensity.",
    },
    "상대성이론과 GNSS 오차 분석": {
        "title": "Relativity and GNSS Error Analysis",
        "description": "Using Python, I calculated special- and general-relativistic time shifts and analyzed why an uncorrected difference of about 38 μs per day could produce roughly 11.4 km of GNSS error.",
    },
    "Pygame 벽돌깨기": {
        "title": "Pygame Brick Breaker",
        "description": "A final Python Programming project that implements object movement, collision detection, scoring, and game-state control with Pygame.",
    },
}

ARCHIVE_TRANSLATIONS = {
    "경사하강법과 SDGs 정책 방향 탐구": {
        "title": "Gradient Descent and SDGs Policy Research",
        "description": "A research paper on mean squared error, weights, learning rates, and local minima, with a review of how optimization could support policy-data prediction.",
    },
    "DNA 컴퓨팅과 데이터 저장": {
        "title": "DNA Computing and Data Storage",
        "description": "A research paper on encoding binary information in DNA, molecular parallelism, high-density storage, and the remaining challenges in I/O speed, retrieval, and cost.",
    },
    "최저임금과 물가 예측": {
        "title": "Minimum Wage and Inflation Prediction",
        "description": "I combined KOSIS consumer-price data with annual minimum-wage records to analyze their relationship and model the direction of price changes.",
    },
    "Django 개인 포트폴리오": {
        "title": "Django Personal Portfolio",
        "description": "I built this responsive portfolio with Django templates, CSS, and vanilla JavaScript and deployed it in a Linux-based Django environment.",
    },
    "Google News RSS 추천기": {
        "title": "Google News RSS Recommender",
        "description": "A Python mini project that reads Google News RSS feeds, scores headlines by weighted keywords, and recommends the most relevant recent articles.",
    },
    "이미지 기반 미로 탐색": {
        "title": "Image-based Maze Solver",
        "description": "I used OpenCV and NumPy to extract walkable paths from a maze image, detect entrances, run BFS, and draw the shortest route on the result image.",
    },
    "2030년 서울 기온 예측": {
        "title": "Seoul Temperature Prediction for 2030",
        "description": "I prepared long-term Seoul temperature records, trained a regression model, and visualized a forecast of future average temperature.",
    },
    "공공자전거 수요 예측": {
        "title": "Public Bike Demand Prediction",
        "description": "I split public-bike data into training and evaluation sets and practiced the full machine-learning workflow for demand prediction.",
    },
    "월별 불쾌지수 분석": {
        "title": "Monthly Discomfort Index Analysis",
        "description": "I processed monthly weather summaries, calculated discomfort-index values, and compared seasonal changes through charts.",
    },
    "인구 데이터 시각화": {
        "title": "Population Data Visualization",
        "description": "I transformed age-group population data with NumPy and Pandas and visualized its distribution for easier comparison.",
    },
    "기상 공공데이터 처리": {
        "title": "Weather Public-data Pipeline",
        "description": "I practiced an end-to-end workflow for selecting, cleaning, aggregating, and visualizing columns from public weather datasets.",
    },
    "원자 모형 시뮬레이터": {
        "title": "Atomic Model Simulator",
        "description": "A Turtle and PySimpleGUI program that calculates and animates electron arrangements for a selected atomic number.",
    },
    "충돌 없는 랜덤 원 배치": {
        "title": "Non-overlapping Random Circle Placement",
        "description": "A geometry program that compares center distances and radii to place randomly generated circles without collisions.",
    },
    "충돌 없는 랜덤 사각형 배치": {
        "title": "Non-overlapping Random Rectangle Placement",
        "description": "A program that checks rectangle coordinates, width, and height to generate a collision-free random layout.",
    },
    "IDA* 루빅스 큐브 풀이": {
        "title": "IDA* Rubik's Cube Solver",
        "description": "I modeled 3×3 cube rotations as arrays and combined a heuristic with iterative-deepening search to find a solution from a scrambled state.",
    },
}

LEARNING_TRANSLATIONS = {
    "Algorithm & Problem Solving": {
        "description": "I document problem-solving approaches from dynamic programming, greedy methods, BFS, DFS, and Dijkstra to CodeUp and BOJ practice.",
    },
    "Data, AI & Science": {
        "description": "I explore public-data analysis, machine learning, gradient descent, DNA computing, relativity, and GNSS from a computing perspective.",
    },
    "Web & Backend": {
        "description": "I am learning full-stack structure from HTML, CSS, and JavaScript DOM work to Django, MySQL, Linux servers, and map APIs.",
    },
    "Programming Foundations": {
        "description": "I practice C/C++ and Python fundamentals, object-oriented programming, file I/O, and GUI development with Tkinter, Turtle, and Pygame.",
    },
}

JOURNEY_TRANSLATIONS = {
    "2023년 부산광역시정보영재교육원 고1정보심화반": {
        "title": "2023 Advanced Information Program at Busan Gifted Computer Education Center",
        "organization": "Busan Gifted Computer Education Center · Completed as Runner-up",
        "award": "GOVERNOR OF EDUCATION AWARD",
        "award_detail": "(Academic Excellence / 2nd Place)",
        "description": "I studied Python, mathematics-based algorithms, and AI theory, then completed projects that turned my interest in computer engineering into a concrete direction.",
    },
    "정보 교과에서 데이터 다루기": {
        "title": "Learning Data through Information Class",
        "organization": "Busanjungang High School · Information Subject",
        "award": "SUBJECT EXCELLENCE AWARD",
        "award_detail": "(1st Place School-wide)",
        "description": "I learned Python fundamentals and processed and visualized monthly discomfort-index and age-group population datasets.",
    },
    "AI 프로젝트로 예측 경험 쌓기": {
        "title": "Building Prediction Experience through AI Projects",
        "organization": "Busanjungang High School · AI Project Club",
        "description": "I analyzed weather and public-bike data and practiced data splitting, training, and evaluation while predicting temperature and bike demand.",
    },
    "경사하강법과 SDGs 정책 방향 탐구": {
        "title": "Gradient Descent and SDGs Policy Research",
        "organization": "Busanjungang High School · Interdisciplinary Research Paper",
        "description": "I examined how gradient descent minimizes model loss, the limits introduced by learning rates, and its possible use in policy-data prediction.",
    },
    "DNA 컴퓨팅과 데이터 저장": {
        "title": "DNA Computing and Data Storage",
        "organization": "Busanjungang High School · Science Research Paper",
        "description": "I studied DNA-based information encoding, parallel computation, and high-density storage, then organized the challenges of I/O speed, retrieval, and cost.",
    },
    "상대성이론이 만드는 위치 정확도": {
        "title": "How Relativity Shapes Positioning Accuracy",
        "organization": "Busanjungang High School · Science Research Paper",
        "description": "I calculated relativistic time shifts for GNSS satellites in Python and analyzed why time correction determines the accuracy of location-based ICT systems.",
    },
    "컴퓨터공학의 기반 다지기": {
        "period": "2026.03 — Present",
        "title": "Building a Computer Engineering Foundation",
        "organization": "Dong-A University · Computer Engineering",
        "description": "Through major courses and a student study group, I continue to learn Python, C/C++, object-oriented programming, and structured problem solving.",
    },
    "2026 기상 빅데이터 콘테스트 참가": {
        "title": "2026 Weather Big Data Contest Participation",
        "organization": "Hosted by the Korea Meteorological Administration · Participant",
        "description": "I experienced defining a problem from weather big data and developing an analysis idea into a project proposal.",
    },
    "2026 NYPC 대회 참가": {
        "title": "2026 NYPC Participation",
        "organization": "Hosted by NEXON · Participant",
        "description": "During the competition period, I practiced analyzing constraints and implementing and validating Python solutions within the time limit.",
    },
    "2026 동아 AI·SW 여름 부트캠프": {
        "title": "2026 Dong-A AI·SW Summer Bootcamp",
        "organization": "Dong-A University National Center of Excellence in Software",
        "description": "I am learning algorithms, MySQL, frontend fundamentals, and Django while building a campus navigation service and this portfolio.",
    },
}

FILTER_LABELS = {
    "ko": {"연구": "Research", "AI · 데이터": "AI & Data", "웹": "Web", "알고리즘": "Algorithms", "Python": "Python"},
    "en": {"연구": "Research", "AI · 데이터": "AI & Data", "웹": "Web", "알고리즘": "Algorithms", "Python": "Python"},
}

UI_TEXT = {
    "ko": {
        "meta_description": "풀스택 웹 개발과 인공지능을 공부하는 {name}의 컴퓨터공학 포트폴리오",
        "home_aria": "홈으로",
        "main_menu": "Main navigation",
        "nav_about": "About",
        "nav_journey": "Journey",
        "nav_projects": "Projects",
        "nav_learning": "Learning",
        "nav_contact": "Contact",
        "theme": "테마 변경",
        "menu_open": "Open menu",
        "menu": "Menu",
        "language_button": "EN",
        "language_aria": "영어로 전환",
        "hero_greeting": "안녕하세요,",
        "hero_suffix": "입니다.",
        "view_projects": "View Projects",
        "current_interest": "현재 관심 분야",
        "panel_line1": "배운 원리를",
        "panel_line2": "코드로 연결합니다.",
        "based_in": "Based in",
        "based_value": "대한민국, 부산광역시",
        "studying": "Major",
        "studying_value": "컴퓨터공학",
        "focus": "Focus",
        "focus_value": "Full-stack · AI · Data",
        "panel_status": "오늘 배운 내용을 코드로 기록 중",
        "about_line": "기초부터 쌓아",
        "about_em": "직접 구현",
        "about_suffix": "합니다.",
        "journey_line": "관심을 코드로 옮긴",
        "journey_em": "성장 과정",
        "journey_suffix": "입니다.",
        "projects_line": "분석하고 설계해",
        "projects_em": "결과로 구현",
        "projects_suffix": "했습니다.",
        "view_details": "view details",
        "project_view": "View Project",
        "research_report": "Research Paper",
        "archive_title": "Project Archive",
        "archive_description": "수업과 탐구에서 완성한 웹·알고리즘·데이터 프로젝트를 기술과 배운 점 중심으로 정리했습니다.",
        "find_category": "Browse by category",
        "total_prefix": "",
        "total_suffix": " items",
        "filter_aria": "Project category filters",
        "all": "All",
        "repository_view": "view README",
        "learning_line": "프로젝트로 확장한",
        "learning_em": "학습 영역",
        "learning_suffix": "입니다.",
        "contact_line": "배움과 아이디어를",
        "contact_em": "함께",
        "contact_suffix": "나눠요.",
        "contact_description": "풀스택, 인공지능, 데이터 프로젝트에 관한 이야기를 편하게 남겨주세요.",
        "social_aria": "소셜 및 연락 채널",
        "name_placeholder": "이름",
        "email_placeholder": "이메일",
        "message_placeholder": "함께 만들고 싶은 이야기를 들려주세요.",
        "send_message": "Send Message",
        "footer_text": "Built with Django. Developed with assistance from OpenAI Codex.",
        "top": "Back to Top",
    },
    "en": {
        "meta_description": "Computer engineering portfolio of {name}, focused on full-stack web development and AI",
        "home_aria": "Go to home",
        "main_menu": "Main navigation",
        "nav_about": "About",
        "nav_journey": "Journey",
        "nav_projects": "Projects",
        "nav_learning": "Learning",
        "nav_contact": "Contact",
        "theme": "Change theme",
        "menu_open": "Open menu",
        "menu": "Menu",
        "language_button": "KR",
        "language_aria": "Switch to Korean",
        "hero_greeting": "Hello, I'm",
        "hero_suffix": ".",
        "view_projects": "View projects",
        "current_interest": "Current interests",
        "panel_line1": "Turning what I learn",
        "panel_line2": "into working code.",
        "based_in": "Based in",
        "based_value": "Busan, South Korea",
        "studying": "Major",
        "studying_value": "Computer Science & Engineering",
        "focus": "Focus",
        "focus_value": "Full-stack · AI · Data",
        "panel_status": "Documenting today's learning in code",
        "about_line": "Building foundations,",
        "about_em": "then implementing",
        "about_suffix": ".",
        "journey_line": "Turning curiosity into code:",
        "journey_em": "my journey",
        "journey_suffix": ".",
        "projects_line": "From analysis and design",
        "projects_em": "to working results",
        "projects_suffix": ".",
        "view_details": "view details",
        "project_view": "View project",
        "research_report": "Research paper",
        "archive_title": "Project Archive",
        "archive_description": "A curated record of substantial web, algorithm, and data projects completed through coursework and independent research.",
        "find_category": "Browse by category",
        "total_prefix": "",
        "total_suffix": " items",
        "filter_aria": "Project category filters",
        "all": "All",
        "repository_view": "view README",
        "learning_line": "Learning expanded",
        "learning_em": "through projects",
        "learning_suffix": ".",
        "contact_line": "Let's share ideas",
        "contact_em": "and keep learning",
        "contact_suffix": ".",
        "contact_description": "Feel free to reach out about full-stack, AI, or data projects.",
        "social_aria": "Social and contact channels",
        "name_placeholder": "Your name",
        "email_placeholder": "Your email",
        "message_placeholder": "Tell me what you would like to build or learn together.",
        "send_message": "Send message",
        "footer_text": "Built with Django. Developed with assistance from OpenAI Codex.",
        "top": "Back to top",
    },
}


def localize_items(items, translations, language):
    localized = deepcopy(items)
    if language == "en":
        for item in localized:
            translation = translations.get(item["title"])
            if translation:
                item.update(translation)
    return localized


def home(request):
    language = "en" if request.GET.get("lang") == "en" else "ko"
    is_english = language == "en"

    profile = deepcopy(PROFILE)
    profile["display_name"] = profile["name"]
    if is_english:
        profile.update(PROFILE_EN)

    copy = deepcopy(UI_TEXT[language])
    copy["meta_description"] = copy["meta_description"].format(name=profile["display_name"])

    stats = deepcopy(STATS)
    stat_labels = ["Projects & research", "Code archives", "Practice solutions"]
    for stat, label in zip(stats, stat_labels):
        stat["label"] = label

    projects = localize_items(PROJECTS, PROJECT_TRANSLATIONS, language)
    project_archive = localize_items(PROJECT_ARCHIVE, ARCHIVE_TRANSLATIONS, language)
    for project in project_archive:
        project["category_label"] = project["category"]

    archive_filters = [
        {"value": value, "label": FILTER_LABELS[language][value]}
        for value in ARCHIVE_FILTERS
    ]

    return render(
        request,
        "home.html",
        {
            "language": language,
            "is_english": is_english,
            "switch_language": "ko" if is_english else "en",
            "copy": copy,
            "profile": profile,
            "social_links": SOCIAL_LINKS,
            "stats": stats,
            "skills": SKILLS,
            "projects": projects,
            "project_archive": project_archive,
            "archive_filters": archive_filters,
            "learning_areas": localize_items(LEARNING_AREAS, LEARNING_TRANSLATIONS, language),
            "journey": localize_items(JOURNEY, JOURNEY_TRANSLATIONS, language),
        },
    )
