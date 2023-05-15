from public_service_employee_application import db
from public_service_employee_application.models import Comment, User

# datetime의 출력 형태를 조정하는 함수
def formal_datetime(value, fmt='%y/%m/%d[%H:%M]'):
    return value.strftime(fmt)


# 글의 댓글 목록을 반환하는 함수
def getComments(value):
    comments = Comment.query.filter(Comment.post_id == value.id).all()
    return comments

def getUser(value):
    user = User.query.get(value.user_id)
    return user