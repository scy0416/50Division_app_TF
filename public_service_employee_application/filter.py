# datetime의 출력 형태를 조정하는 함수
def formal_datetime(value, fmt='%y/%m/%d[%H:%M]'):
    return value.strftime(fmt)