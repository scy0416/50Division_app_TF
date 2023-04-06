# datetime의 출력 형태를 조정하는 함수
def formal_datetime(value, fmt='%Y년 %m월 %d일 %H:%H'):
    return value.strftime(fmt)