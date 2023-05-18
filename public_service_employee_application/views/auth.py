from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
from datetime import datetime
import functools

from public_service_employee_application.models import User, Join_request
from public_service_employee_application import db


# 블루프린트 객체 생성
bp = Blueprint('auth', __name__, url_prefix='/auth')


# 이 블루프린트의 최초 진입점
@bp.route('/login', methods=['GET'])
def index():
    return render_template('auth/login.html')


# 로그인 처리
@bp.route('/login', methods=['POST'])
def login():
    userid = request.form.get('id')
    password = request.form.get('password')

    user = User.query.filter(User.userid == userid).first()

    if not user:
        flash("존재하지 않는 사용자입니다.")
        return redirect(url_for('auth.index'))
    elif user.password == password and user.role == 'ADMIN':
        session.clear()
        session['user_id'] = user.id
        session['isAdmin'] = True
        return redirect(url_for('admin.index'))
    elif user.password == password and user.role == 'USER':
        session.clear()
        session['user_id'] = user.id
        session['isAdmin'] = False
        return redirect(url_for('employee.index'))
    flash("알 수 없는 오류가 발생했습니다")
    return redirect(url_for('auth.index'))


# 로그아웃
@bp.route('/logout', methods=['GET'])
def logout():
    # 로그인 되어있던 정보를 리셋시킨다.
    session.clear()
    return redirect(url_for('main.index'))


# 가입 페이지
@bp.route('/join', methods=['GET'])
def join_page():
    return render_template('auth/join.html')


# 가입 신청
@bp.route('/join', methods=['POST'])
def request_join():
    name = request.form.get('name')
    birth_date =  request.form.get('birth_date')
    userid = request.form.get('id')
    password = request.form.get('password')

    join_request = Join_request(
        userid=userid,
        password=password,
        name=name,
        birth_date=birth_date,
        state='WAITING',
        request_date=datetime.now()
    )

    db.session.add(join_request)
    db.session.commit()

    return redirect(url_for('auth.index'))


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
def login_required_admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # g객체에 유저의 정보가 없다면
        if g.user is None:
            # 로그인화면으로 리디렉션 시킨다.
            return redirect(url_for('auth.index'))
        # 관리자가 아니라면
        elif g.user.role != 'ADMIN':
            # 공무직원메인화면으로 리디렉션 시킨다.
            return redirect(url_for('employee.index'))
        return view(**kwargs)
    return wrapped_view


# 직원인지 확인하는 래퍼 메소드
# 로그인 되어있지 않다면 로그인 화면으로 리디렉션 되고, 직원이 아니라면 적절한 화면으로 리디렉션 된다.
def login_required_employee(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # g객체에 유저의 정보가 없다면
        if g.user is None:
            # 로그인화면으로 리디렉션 시킨다.
            return redirect(url_for('auth.index'))
        # 공무직원이 아니라면
        elif g.user.role != 'USER':
            # 관리자 메인화면으로 리디렉션 시킨다.
            return redirect(url_for('admin.index'))
        return view(**kwargs)
    return wrapped_view