from flask import Blueprint, session, redirect, url_for

# 블루프린트 객체 생성
bp = Blueprint('main', __name__, url_prefix='/')


# 웹 페이지에 최초로 진입하는 부분
@bp.route('/', methods=['GET'])
def index():
    # 관리자인 경우
    if session.get('isAdmin') == True:
        # 관리자 메인화면으로 리디렉션
        return redirect(url_for('admin.index'))
    # 공무직원인 경우
    elif (session.get('isAdmin') is False) and (session.get('user_id') is not None):
        # 공무직원 메인화면으로 리디렉션
        return redirect(url_for('employee.index'))
    # 로그인 되어있지 않은 경우
    elif session.get('user_id') is None:
        # 로그인 화면으로 리디렉션
        return redirect(url_for('auth.index'))
    session.clear()
    return redirect(url_for('main.index'))