from flask import Blueprint, request, render_template, g, redirect, url_for
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import Post, User, Comment
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('employee_notice', __name__, url_prefix='/employee/notice')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    notice_list = Post.query.outerjoin(
        User,
        Post.user_id == User.id
    ).filter(
        User.role == 'ADMIN'
    ).filter(
        Post.subject.contains(q)
    ).order_by(
        Post.create_date.desc()
    ).paginate(page=page, per_page=10)

    return render_template('employee/notice/notice_list.html',
                           notice_list=notice_list, q=q, page=page)


# 공지사항 상세 페이지
@bp.route('/<int:post_id>', methods=['GET'])
@login_required_employee
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter(
        Comment.post_id == post.id
    ).order_by(
        Comment.create_date.asc()
    ).all()

    return render_template('employee/notice/notice_detail.html',
                           post=post, comments=comments)


# 댓글 수정
@bp.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required_employee
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')

    comment.content = content
    comment.modify_date = datetime.now()

    db.session.commit()

    return '', 204


# 댓글 생성
@bp.route('/comment/<int:post_id>/create', methods=['POST'])
@login_required_employee
def create_comment(post_id):
    content = request.form.get('content')
    comment = Comment(
        user_id=g.user.id,
        post_id=post_id,
        content=content,
        create_date=datetime.now()
    )
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('employee_notice.detail', post_id=post_id))


# 댓글 삭제
@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required_employee
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('employee_notice.detail', post_id=post_id))