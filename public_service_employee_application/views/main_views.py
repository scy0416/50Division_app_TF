from flask import Blueprint, url_for, session, request
from werkzeug.utils import redirect

# 블루 프린트 객체 생성
bp = Blueprint('main', __name__, url_prefix='/')

# 웹 페이지에 최초로 진입하는 부분
# TODO 이 부분에서 다른 부분으로 리디렉션 시키는 것을 지향하기 위해 나중에는 각각 적절한 곳으로 리디렉션 할 수 있도록 바꾸도록 한다.
@bp.route('/', methods=('GET', ))
def index():
    # GET메소드인 경우, 어드민인 경우
    if request.method == 'GET' and session.get('isAdmin') == True:
        # 어드민 메인화면으로 리디렉션
        return redirect(url_for('admin.index'))
    # GET메소드인 경우, 어드민이 아니고, 로그인을 한 상황인 경우
    elif (request.method == 'GET') and (session.get('isAdmin') == False) and (session.get('user_id') is not None):
        # 일반직원 메인화면으로 리디렉션
        return redirect(url_for('employee.index'))
    # GET메소드인 경우, 로그인하지 않은 경우
    elif (request.method == 'GET') and (session.get('user_id') is None):
        # 로그인 화면으로 리디렉션
        return redirect(url_for('auth.login'))
    #return redirect(url_for('auth.login'))