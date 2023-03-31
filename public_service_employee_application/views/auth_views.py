import functools
from flask import Blueprint, request, render_template, session, url_for, flash, g
from werkzeug.utils import redirect

from public_service_employee_application.forms import UserLoginForm
from public_service_employee_application.models import User

# 블루프린트 객체 생성
bp = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 화면에 대한 요청으로 GET메소드는 로그인 화면 요청, POST메소드는 로그인 처리 요청이다.
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    # 유처 로그인 폼을 생성
    form = UserLoginForm()
    # 로그인 화면을 요구하는 경우
    if request.method == 'GET':
        # auth/login.html을 출력
        return render_template('auth/login.html', form=form)
    # 로그인 처리를 요청하는 경우
    elif request.method == 'POST' and form.validate_on_submit():
        # 에러 초기화
        error = None
        # id를 가지고 데이터를 뽑아내는 과정
        user = User.query.filter_by(userid=form.id.data).first()
        # 해당 id를 가진 유저가 없는 경우
        if not user:
            error = "존재하지 않는 사용자입니다."
        # 로그인한 유저가 관리자인 경우
        # 이 부분 역시 정적으로 확인할 것이 아니라 데이터베이스로부터 값을 가져와서 확인해야 한다.
        # TODO 이 부분을 데이터베이스에서 가져온 값으로 처리하도록 만들기(관리자 계정을 만든 이후)
        elif form.password.data == user.password and user.role == 'ADMIN':
            # 세션 초기화
            session.clear()
            # 세션에 id정보 저장
            session['user_id'] = user.id
            # 세션에 어드민 정보 저장
            session['isAdmin'] = True
            # 메인으로 리디렉션
            return redirect(url_for('main.index'))
        # 로그인한 유저가 일반유저인 경우
        # 입력한 id가 유저의 id와 같고, 비밀번호가 그냥 같은 경우
        # TODO 이 부분도 비밀번호를 암호화하여 가져올 수 있어야 한다.
        elif form.password.data == user.password and user.role == 'USER':
            session.clear()
            session['user_id'] = user.id
            session['isAdmin'] = False
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)

# 로그아웃을 처리하는 부분
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# 요청이 처리되기 전에 실행되는 어노테이션으로 로그인 된 정보가 존재한다면 로그인 된 사용자의 정보를 g.user에 담고 없으면 None을 저장한다.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

# 관리자인지 확인하는 래퍼 메소드
# 로그인 되어있지 않다면 로그인 화면으로 리디렉션 되고, 관리자가 아니라면 적절한 화면으로 리디렉션 된다.
def login_required_admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('main.index'))
        elif g.user.role != 'ADMIN':
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view

# 직원인지 확인하는 래퍼 메소드
# 로그인 되어있지 않다면 로그인 화면으로 리디렉션 되고, 직원이 아니라면 적절한 화면으로 리디렉션 된다.
def login_required_employee(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('main.index'))
        elif g.user.role != 'USER':
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view