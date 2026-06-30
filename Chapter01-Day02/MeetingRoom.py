def meeting_room(meettings):
    # 회의 종료 시간이 빠른 순서로 정렬
    meettings.sort(key=lambda x : x[1])     # lambda는 휘발성 --> sort 후에는 사라져서 메모리 이득

    # (지역)변수 선언
    count = 0
    end_time = 0
    selected = []

    # 이전 회의가 끝난 후 회의가 시작하는 회의 선택
    for start, end in meettings:
        if start >= end_time:
            selected.append((start, end))
            count += 1
            end_time = end

    return count, selected

# 예정된 회의 목록 추가
meetings = [(1,4), (3,5), (0,6), (5,7), (8,9)]

# 값 출력
count, selected = meeting_room(meetings)
print(count)
print(selected)
