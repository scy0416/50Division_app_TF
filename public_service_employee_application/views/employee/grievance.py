from flask import Blueprint, render_template, request, g, redirect, url_for
from datetime import datetime

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import Post, Comment, User
from public_service_employee_application import db


# 블루 프린트 객체 생성
bp = Blueprint('employee_grievance', __name__, url_prefix='/employee/grievance')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    grievance_list = db.session.query(Post).outerjoin(
        User,
        Post.user_id == User.id
    ).filter(
        User.id == g.user.id
    ).filter(
        Post.subject.contains(q)
    ).order_by(Post.create_date.desc())
    grievance_list = grievance_list.paginate(page=page, per_page=10)

    return render_template('employee/grievance/grievance_list.html',
                           q=q, page=page, grievance_list=grievance_list)


# 고출 글 상세 보기
@bp.route('/<int:post_id>', methods=['GET'])
@login_required_employee
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    comments = Comment.query.filter(Comment.post_id == post.id).order_by(
        Comment.create_date
    ).all()

    return render_template('employee/grievance/grievance_detail.html',
                           post=post, user=user, comments=comments)

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

    return redirect(url_for('employee_grievance.detail', post_id=post_id))


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

# 댓글 삭제
@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required_employee
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('employee_grievance.detail', post_id=post_id))


# 고충 글 편집 페이지
@bp.route('/<int:post_id>/edit', methods=['GET'])
@login_required_employee
def get_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('employee/grievance/grievance_edit.html', post=post)


# 고충 글 편집
@bp.route('<int:post_id>/edit', methods=['POST'])
@login_required_employee
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    subject = request.form.get('subject')
    content = request.form.get('content')
    post.subject = subject
    post.content = content
    db.session.commit()
    return redirect(url_for('employee_grievance.detail', post_id=post_id))


# 고충 글 삭제
@bp.route('<int:post_id>/delete', methods=['POST'])
@login_required_employee
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('employee_grievance.index'))


# 고충 글 작성 페이지
@bp.route('/write', methods=['GET'])
@login_required_employee
def write():
    return render_template('employee/grievance/grievance_write.html')


# 고충 글 등록
@bp.route('/write/post', methods=['POST'])
@login_required_employee
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

    return redirect(url_for('employee_grievance.index'))