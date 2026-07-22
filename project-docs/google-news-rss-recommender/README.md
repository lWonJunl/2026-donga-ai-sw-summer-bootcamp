# Google News RSS 추천기

사용자가 입력한 관심 키워드로 최근 Google News RSS 기사를 수집하고 관련도를 계산해 상위 기사를 추천하는 Python 미니 프로젝트입니다.

## 주요 기능

- 쉼표로 구분한 여러 검색 키워드를 우선순위 순서로 입력받습니다.
- Google News RSS에서 최근 7일의 한국어 기사를 불러옵니다.
- 제목에 포함된 키워드의 순서와 개수에 따라 관련도 점수를 계산합니다.
- 현재 남은 기사 중 점수가 가장 높은 기사를 반복 선택해 최대 5개를 추천합니다.

## 기술

`Python` · `Feedparser` · `RSS` · `Keyword Scoring` · `Greedy Selection`

## 관련 파일

- [Python 소스](../../Chapter01-Day02/MiniProject-RecommandNews.py)

## 배운 점

외부 RSS 데이터를 읽고 사용자의 입력을 검색 조건으로 변환하는 방법을 익혔습니다. 단순 키워드 포함 여부를 점수 모델로 확장하면서 추천 기준을 코드로 표현해 봤습니다.
