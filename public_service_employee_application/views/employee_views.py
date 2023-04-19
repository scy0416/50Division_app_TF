from flask import Blueprint, render_template, request, session, redirect, url_for
from sqlalchemy import and_
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application import db
from public_service_employee_application.models import Post, User, Comment
from public_service_employee_application.forms import writeForm, contentForm

# 블루프린트 객체 생성
bp = Blueprint('employee', __name__, url_prefix='/employee')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET', ))
# 직원으로 로그인이 되었나 확인하는 부분
@login_required_employee
def index():
    return render_template('user/employee_main.html')

# 공지사항
@bp.route('/notice/', methods=('GET', 'POST'))
@login_required_employee
def notice():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    notice_list = db.session.query(Post).join(User).filter(and_(User.role == 'ADMIN', Post.subject.contains(q))).order_by(Post.create_date.desc())
    notice_list = notice_list.paginate(page=page, per_page=10)

    # 템플릿 출력
    return render_template('user/notice_list.html', notice_list=notice_list, q=q, page=page)

# 공지사항 상세창
@bp.route('/notice/<int:post_id>', methods=('GET', ))
@login_required_employee
def notice_detail(post_id):
    # 폼 생성
    form = writeForm()
    cForm = contentForm()

    post = Post.query.get_or_404(post_id)
    return render_template('user/notice_detail.html', post=post, form=form, cForm=cForm)

# 댓글 등록
@bp.route('/comment', methods=('POST', ))
@login_required_employee
def create_comment():
    form = writeForm()
    if form.validate_on_submit():
        comment = Comment(
            user_id=session.get('user_id'),
            post_id=request.form.get('post_id'),
            content=form.content.data,
            create_date=datetime.now()
        )
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('employee.notice_detail', post_id=request.form.get('post_id')))

# 댓글 수정
@bp.route('/comment/<int:comment_id>/edit', methods=('POST', ))
@login_required_employee
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    comment.content = request.form.get('content')
    comment.modify_date = datetime.now()
    db.session.commit()
    return redirect(url_for('employee.notice_detail', post_id=post_id))

# 댓글 삭제
@bp.route('/comment/<int:comment_id>/delete', methods=('POST', ))
@login_required_employee
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('employee.notice_detail', post_id=post_id))

# 인사정보 조회
@bp.route('/pr/<int:user_id>', methods=('GET', ))
@login_required_employee
def pr_information(user_id):
    user = User.query.get_or_404(user_id)

    return render_template('user/user_detail.html', user=user)