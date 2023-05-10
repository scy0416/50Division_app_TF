from flask import Blueprint, request, render_template, jsonify, g, redirect, url_for
from sqlalchemy import and_, desc
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import Post, User, Comment
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_notice', __name__, url_prefix='/admin/notice')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    notice_list = Post.query.outerjoin(User, Post.user_id == User.id).filter(
        and_(
            User.role == 'ADMIN',
            Post.subject.contains(q)
        )
    ).order_by(desc(Post.create_date))
    notice_list = notice_list.paginate(page=page, per_page=10)

    return render_template('admin/notice/notice_list.html', notice_list=notice_list, q=q, page=page)


# 글 작성 페이지
@bp.route('/write', methods=['GET'])
@login_required_admin
def write():
    return render_template('admin/notice/notice_write.html')


# 글 작성 처리
@bp.route('/write/post', methods=['POST'])
@login_required_admin
def create_post():
    subject = request.form.get('subject')
    content = request.form.get('content')
    post = Post(
        user_id=g.user.id,
        subject=subject,
        content=content,
        create_date=datetime.now()
    )
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('admin_notice.index'))

# 글 상세 보기
@bp.route('/<int:post_id>', methods=['GET'])
@login_required_admin
def detail(post_id):
    post = db.session.query(Post, User).select_from(Post).outerjoin(
        User,
        Post.user_id == User.id
    ).filter(
        Post.id == post_id
    ).first()

    comments = db.session.query(Comment, User).select_from(Comment).outerjoin(
        User,
        Comment.user_id == User.id
    ).filter(
        Comment.post_id == post_id
    ).order_by(Comment.create_date).all()

    return render_template('admin/notice/notice_detail.html', post=post, comments=comments)


# 댓글 수정
@bp.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required_admin
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')

    comment.content = content
    comment.modify_date = datetime.now()

    db.session.commit()

    return '', 204

# 댓글 생성
@bp.route('/comment/<int:post_id>/create', methods=['POST'])
@login_required_admin
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

    return redirect(url_for('admin_notice.detail', post_id=post_id))


# 댓글 삭제
@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required_admin
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()

    post_id = request.form.get('post_id')

    return redirect(url_for('admin_notice.detail', post_id=post_id))


# 공지사항 수정 페이지
@bp.route('<int:post_id>/edit', methods=['GET'])
@login_required_admin
def get_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('admin/notice/notice_edit.html', post=post)


# 공지사항 수정
@bp.route('<int:post_id>/edit', methods=['POST'])
@login_required_admin
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    subject = request.form.get('subject')
    content = request.form.get('content')
    post.subject = subject
    post.content = content
    db.session.commit()
    return redirect(url_for('admin_notice.detail', post_id=post_id))


# 공지사항 삭제
@bp.route('<int:post_id>/delete', methods=['POST'])
@login_required_admin
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin_notice.index'))