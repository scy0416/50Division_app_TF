import os
from flask import Blueprint, render_template, request, session, redirect, url_for, g, send_from_directory, jsonify
from sqlalchemy import and_
from datetime import datetime
from werkzeug.utils import secure_filename

from public_service_employee_application.views.auth_views import login_required_employee

from sqlalchemy import and_
from public_service_employee_application import db
from public_service_employee_application.models import Post, User, Comment, HR_change_request, Vacation_request, Quarter, Wellfare_point, Medical_checkup_request
from public_service_employee_application.forms import writeForm, contentForm

# 블루프린트 객체 생성
bp = Blueprint('employee', __name__, url_prefix='/employee')


# 이 블루프린트의 최초 진입점
@bp.route('/', methods=('GET',))
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
    notice_list = db.session.query(Post).join(User).filter(
        and_(User.role == 'ADMIN', Post.subject.contains(q))).order_by(Post.create_date.desc())
    notice_list = notice_list.paginate(page=page, per_page=10)

    # 템플릿 출력
    return render_template('user/notice_list.html', notice_list=notice_list, q=q, page=page)


# 공지사항 상세창
@bp.route('/notice/<int:post_id>', methods=('GET',))
@login_required_employee
def notice_detail(post_id):
    # 폼 생성
    form = writeForm()
    cForm = contentForm()

    post = Post.query.get_or_404(post_id)
    return render_template('user/notice_detail.html', post=post, form=form, cForm=cForm)


# 댓글 등록
@bp.route('/notice/comment', methods=('POST', ))
@login_required_employee
def create_comment_notice():
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
@bp.route('/notice/comment/<int:comment_id>/edit', methods=('POST', ))
@login_required_employee
def edit_comment_notice(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    comment.content = request.form.get('content')
    comment.modify_date = datetime.now()
    db.session.commit()
    return redirect(url_for('employee.notice_detail', post_id=post_id))


# 댓글 삭제
@bp.route('/notice/comment/<int:comment_id>/delete', methods=('POST', ))
@login_required_employee
def delete_comment_notice(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('employee.notice_detail', post_id=post_id))


# 인사정보 조회
@bp.route('/pr/<int:user_id>', methods=('GET',))
@login_required_employee
def pr_information(user_id):
    user = User.query.get_or_404(user_id)

    return render_template('user/user_detail.html', user=user)


# 인사정보 변경
@bp.route('pr/<int:user_id>/edit', methods=('POST',))
@login_required_employee
def edit_pr_information(user_id):
    user = User.query.get_or_404(user_id)

    phone_num = request.form.get("phone_num")
    address = request.form.get("address")

    user.phone_num = phone_num
    user.address = address

    db.session.commit()
    return redirect(url_for('employee.pr_information', user_id=user_id))


# 인사정보 변경 신청
@bp.route('pr/<int:user_id>/hr_edit', methods=('POST',))
@login_required_employee
def require_edit_pr(user_id):
    type = None
    if request.form.get('type') == 'hire_date':
        type = 'HIRE'
    elif request.form.get('type') == 'retirement_date':
        type = 'RETIREMENT'
    hr_change_request = HR_change_request(
        user_id=user_id,
        reason=request.form.get('reason'),
        change_to=request.form.get('change_to'),
        type=type,
        state="WAITING",
        request_date=datetime.now()
    )
    db.session.add(hr_change_request)
    db.session.commit()

    return redirect(url_for('employee.pr_information', user_id=user_id))


# 휴가 신청
@bp.route('/vacation/', methods=('GET',))
@login_required_employee
def vacation():
    page = request.args.get('page', type=int, default=1)
    vacation_request_list = Vacation_request.query.filter_by(user_id=g.user.id).order_by(
        Vacation_request.request_date.desc())
    vacation_request_list = vacation_request_list.paginate(page=page, per_page=5)
    return render_template('user/vacation.html', page=page, vacation_request_list=vacation_request_list)


# 휴가 신청 등록
@bp.route('/vacation/', methods=('POST',))
@login_required_employee
def create_vacation_request():
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    reason = request.form.get('reason')
    vacation_request = Vacation_request(
        user_id=g.user.id,
        from_date=from_date,
        to_date=to_date,
        reason=reason,
        state='WAITING',
        request_date=datetime.now()
    )
    db.session.add(vacation_request)
    db.session.commit()
    return redirect(url_for('employee.vacation'))

# 복지 포인트 조회
@bp.route('/welfare/', methods=('GET', ))
@login_required_employee
def welfare():
    quarter_id = request.args.get('quarter_id', type=int, default=-1)
    quarter = None

    quarter_list = Quarter.query.all()

    if quarter_id == -1:
        quarter = Quarter.query.order_by(Quarter.quarter.desc()).first()
        quarter_id = quarter.id
    else:
        quarter = Quarter.query.get_or_404(quarter_id)

    welfare_point = Wellfare_point.query.filter_by(user_id=g.user.id, quarter_id=quarter_id).first()

    return render_template('user/welfare_point.html', quarter_list=quarter_list, quarter=quarter, welfare=welfare_point)

# 의무 교육 현황
@bp.route('/edu/', methods=('GET', ))
@login_required_employee
def edu():
    user = User.query.get_or_404(g.user.id)
    return render_template('user/edu.html', user=user)

# 고충 글 리스트
@bp.route('/grievance', methods=('GET', ))
@login_required_employee
def grievance_list():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    # 검색 처리 과정
    # 실질적인 검색
    grievance = db.session.query(Post).join(User).filter(and_(User.id == g.user.id, Post.subject.contains(q))).order_by(Post.create_date.desc())
    grievance = grievance.paginate(page=page, per_page=10)

    # 템플릿 출력
    return render_template('user/grievance_list.html', grievance_list=grievance, q=q, page=page)

# 고충 글 작성 페이지
@bp.route('/grievance/write', methods=('GET', ))
@login_required_employee
def grievance_write():
    return render_template('user/write.html')

# 고충 글 작성
@bp.route('/grievance/write', methods=('POST', ))
@login_required_employee
def post_grievance():
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
    return redirect(url_for('employee.grievance_list'))

# 고충 글 상세 창
@bp.route('/grievance/<int:post_id>', methods=('GET', ))
@login_required_employee
def grievance_detail(post_id):
    # 확인하려는 글
    post = Post.query.get_or_404(post_id)
    # 템플릿 출력
    return render_template('user/grievance_detail.html', post=post)

# 댓글 작성
@bp.route('/grievance/comment', methods=('POST', ))
@login_required_employee
def create_comment_grievance():
    comment = Comment(
        user_id=g.user.id,
        post_id=request.form.get('post_id'),
        content=request.form.get('content'),
        create_date=datetime.now()
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('employee.grievance_detail', post_id=request.form.get('post_id')))

# 댓글 편집
@bp.route('/grievance/comment/<int:comment_id>/edit', methods=('POST', ))
@login_required_employee
def edit_comment_grievance(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.content = request.form.get('content')
    comment.modify_date = datetime.now()
    db.session.commit()
    return redirect(url_for('employee.grievance_detail', post_id=request.form.get('post_id')))

# 댓글 삭제
@bp.route('/grievance/comment/<int:comment_id>/delete', methods=('POST', ))
@login_required_employee
def delete_comment_grievance(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('employee.grievance_detail', post_id=request.form.get('post_id')))


# 건강검진 확인 요청 화면
@bp.route('/medical_checkup', methods=('GET', ))
@login_required_employee
def medical_checkup():
    page = request.args.get('page', default=1)
    medical_checkup_list = Medical_checkup_request.query.filter_by(user_id=g.user.id).order_by(Medical_checkup_request.request_date.desc())
    medical_checkup_list = medical_checkup_list.paginate(page=page, per_page=10)

    return render_template('user/medical_checkup.html', page=page, medical_checkup_list=medical_checkup_list)

# 건강검진 등록 화면
@bp.route('/medical_checkup/request', methods=('GET', ))
@login_required_employee
def medical_checkup_request_page():
    return render_template('user/medical_checkup_request.html')

# 이미지 업로드 및 건강검진 확인 요청 생성
@bp.route('/medical_checkup', methods=('POST', ))
@login_required_employee
def medical_checkup_request():
    f = request.files['file']
    f.save(os.path.join('static/medical_checkup', secure_filename(f.filename)))

    medical_checkup_request = Medical_checkup_request(
        user_id=g.user.id,
        img_addr=secure_filename(f.filename),
        state='WAITING',
        request_date=datetime.now()
    )
    db.session.add(medical_checkup_request)
    db.session.commit()

    return redirect(url_for('employee.medical_checkup'))

# 건강검진 이미지 미리보기 url
@bp.route('/medical_checkup/<int:request_id>/get_url', methods=('GET', ))
@login_required_employee
def get_image_url(request_id):
    #print("실행")
    medical_checkup_request = Medical_checkup_request.query.get_or_404(request_id)
    image_url = medical_checkup_request.img_addr
    #return jsonify({"url": image_url})
    return jsonify(({"url": url_for('employee.medical_checkup_preview', filename=image_url)}))

# 건강검진 이미지 미리보기
@bp.route('/medical_checkup/<path:filename>/preview', methods=('GET', ))
@login_required_employee
def medical_checkup_preview(filename):
    return send_from_directory('static/medical_checkup', filename)
