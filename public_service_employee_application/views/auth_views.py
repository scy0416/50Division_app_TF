import functools
from flask import Blueprint, request, render_template, session, url_for, flash, g
from werkzeug.utils import redirect
from datetime import datetime

from public_service_employee_application.forms import UserLoginForm, joinForm
from public_service_employee_application.models import User, Join_request
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 화면에 대한 요청으로 GET메소드는 로그인 화면 요청, POST메소드는 로그인 처리 요청이다.
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    # 유처 로그인 폼을 생성
    form = UserLoginForm()
    # 가입 신청 폼 생성
    join_form = joinForm()

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
        # 암호화는 자바스크립트에서 하도록 바꾸기로 한다.
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
    # 로그인 되어있던 정보를 리셋시킨다.
    session.clear()
    return redirect(url_for('main.index'))


@bp.route('/join', methods=['GET'])
def get_join_page():
    return render_template('auth/join.html')


@bp.route('/join', methods=['POST'])
def request_join():
    name = request.form.get('name')
    birth_date = request.form.get('birth_date')
    id = request.form.get('id')
    password = request.form.get('password')

    join_request = Join_request(
        userid=id,
        password=password,
        name=name,
        birth_date=birth_date,
        state='WAITING',
        request_date=datetime.now()
    )

    db.session.add(join_request)
    db.session.commit()

    return redirect(url_for('main.index'))


# 요청이 처리되기 전에 실행되는 어노테이션으로 로그인 된 정보가 존재한다면 로그인 된 사용자의 정보를 g.user에 담고 없으면 None을 저장한다.
@bp.before_app_request
def load_logged_in_user():
    # 세션에 로그인된 유저의 식별용id를 가져온다.
    user_id = session.get('user_id')
    # 로그인 되어있지 않다면
    if user_id is None:
        # g객체의 user에는 아무것도 담기지 않는다.
        g.user = None
    # 로그인 되어있다면
    else:
        # g객체의 user에 유저 정보를 담는다.
        g.user = User.query.get(user_id)

# 관리자인지 확인하는 래퍼 메소드
# 로그인 되어있지 않다면 로그인 화면으로 리디렉션 되고, 관리자가 아니라면 적절한 화면으로 리디렉션 된다.
# TODO 무지성 리디렉션을 정리해야 한다.
def login_required_admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # g객체에 유저의 정보가 없다면
        if g.user is None:
            # 메인화면으로 리디렉션 시킨다.
            return redirect(url_for('main.index'))
        # 관리자가 아니라면
        elif g.user.role != 'ADMIN':
            # 메인화면으로 리디렉션 시킨다.
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view

# 직원인지 확인하는 래퍼 메소드
# 로그인 되어있지 않다면 로그인 화면으로 리디렉션 되고, 직원이 아니라면 적절한 화면으로 리디렉션 된다.
def login_required_employee(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # g객체에 유저의 정보가 없다면
        if g.user is None:
            # 메인화면으로 리디렉션 시킨다.
            return redirect(url_for('main.index'))
        # 공무직원이 아니라면
        elif g.user.role != 'USER':
            # 메인화면으로 리디렉션 시킨다.
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view