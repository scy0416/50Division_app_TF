from public_service_employee_application import db
from sqlalchemy import Column, Integer, CHAR, String, DateTime, Text, ForeignKey, Date


# 유저테이블에 대한 모델
class User(db.Model):
    # 테이블명
    __tablename__ = 'tb_user'
    # 이미 존재하는 테이블에 대한 모델 생성
    __table_args__ = {'extend_existing': True}

    # 사용자 실별용id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 로그인id
    userid = Column(String(128), nullable=True)
    # 이름
    name = Column(String(128), nullable=True)
    # 비밀번호
    password = Column(String(128), nullable=True)
    # 부대명
    unit_name = Column(String(128), nullable=True)
    # 직책
    position = Column(String(128), nullable=True)
    # 생년월일
    birth_date = Column(Date(), nullable=True)
    # 채용일
    hire_date = Column(Date(), nullable=True)
    # 퇴직일
    retirement_date = Column(Date(), nullable=True)
    # 고용형태(PUBLIC_SERVICE/FIXED_TERM/SHORT_TERM)
    employment_type = Column(String(128), nullable=True)
    # 휴가
    vacation = Column(Integer, nullable=True)
    # 건강검진
    medical_checkup = Column(CHAR(50), nullable=True, default='N')
    # 성희롱 예방 교육
    sexual_harassment_prevent = Column(CHAR(50), nullable=True, default='N')
    # 장애인식 개선 교육
    disability_awareness_improvement = Column(CHAR(50), nullable=True, default='N')
    # 직장 내 괴롭힘 예방 교육
    workplace_harassment_prevent = Column(CHAR(50), nullable=True, default='N')
    # 비고
    bigo = Column(String(128), nullable=True)
    # 사용자구분(USER/ADMIN)
    role = Column(String(128), nullable=True, default='USER')


# 가입 신청에 대한 모델
class Join_request(db.Model):
    __tablename__ = 'tb_join_request'
    __table_args__ = {'extend_existing': True}

    # 식별용id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 신청자id
    userid = Column(String(128), nullable=True)
    # 신청 비밀번호
    password = Column(String(128), nullable=True)
    # 신청자 이름
    name = Column(String(128), nullable=True)
    # 신청자 생년월일
    birth_date = Column(Date, nullable=True)
    # 상태(ALLOWED/REJECTED/WAITING)
    state = Column(String(10), nullable=True)
    # 신청일시
    request_date = Column(DateTime, nullable=True)
    # 처리일시
    proc_date = Column(DateTime, nullable=True)


# 복지 포인트에 대한 모델
class Wellfare_point(db.Model):
    __tablename__ = 'tb_welfare_point'
    __table_args__ = {'extend_existing': True}

    # 식별용 id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 부여된 사용자의 식별용id(외래키)
    user_id = Column(Integer, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=False)
    # 외래키가 참조하는 모델로 'wellfare_point_set'으로 역참조가 가능
    user = db.relationship('User', backref=db.backref('wellfare_point_set'))
    # 분기
    quarter = Column(String(128), nullable=True)
    # 지급된 포인트
    point = Column(Integer, nullable=True)


# 게시물들에 대한 모델
class Post(db.Model):
    __tablename__ = 'tb_post'
    __table_args__ = {'extend_existing': True}

    # 게시물 식별용 id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 작성자id(외래키)
    user_id = Column(Integer, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=True)
    # 외래키가 참조하는 모델로 'post_set'으로 역참조가 가능
    user = db.relationship('User', backref=db.backref('post_set'))
    # 제목
    subject = Column(String(128), nullable=True)
    # 내용
    content = Column(String(128), nullable=True)
    # 생성 시간
    create_date = Column(DateTime, nullable=True)
    # 편집 시간
    modify_date = Column(DateTime, nullable=True)


# 댓글들에 대한 모델
class Comment(db.Model):
    __tablename__ = 'tb_comment'
    __table_args__ = {'extend_existing': True}

    # 식별용 id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 작성자id(외래키)
    user_id = Column(Integer, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=True)
    # 외래키가 참조하는 모델로 'comment_set_user'으로 역참조가 가능
    user = db.relationship('User', backref=db.backref('comment_set_user'))
    # 게시글id(외래키)
    post_id = Column(Integer, ForeignKey('tb_post.id', ondelete='CASCADE'), nullable=True)
    # 외래키가 참조하는 모델로 'comment_set_post'으로 역참조가 가능
    post = db.relationship('Post', backref=db.backref('comment_set_post'))
    # 제목
    subject = Column(String(128), nullable=True)
    # 내용
    content = Column(String(128), nullable=True)
    # 생성 시간
    create_date = Column(DateTime, nullable=True)
    # 편집 시간
    modify_date = Column(DateTime, nullable=True)


# 인사정보 변경 신청에 대한 모델
class HR_change_request(db.Model):
    __tablename__ = 'tb_hr_change_request'
    __table_args__ = {'extend_existing': True}

    # 식별용id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 신청자 식별용id(외래키)
    user_id = Column(Integer, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=True)
    # 외래키가 참조하는 모델로 'hr_change_request_set'으로 역참조가 가능
    user = db.relationship('User', backref=db.backref('hr_change_request_set'))
    # 사유
    reason = Column(String(128), nullable=True)
    # 바꾸기를 원하는 날짜
    change_to = Column(Date, nullable=True)
    # 요청 타입(HIRE/RETIREMENT)
    type = Column(String(128), nullable=True)
    # 상태(ALLOWED/REJECTED/WAITING)
    state = Column(String(10), nullable=True)
    # 신청일시
    request_date = Column(DateTime, nullable=True)
    # 처리일시
    proc_date = Column(DateTime, nullable=True)


# 휴가 신청에 대한 모델
class Vacation_request(db.Model):
    __tablename__ = 'tb_vacation_request'
    __table_args__ = {'extend_existing': True}

    # 식별용id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 신청자id(외래키)
    user_id = Column(Integer, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=True)
    # 외래키가 참조하는 모델로 'vacation_request_set'으로 역참조가 가능
    user = db.relationship('User', backref=db.backref('vacation_request_set'))
    # 휴가 시작일
    from_date = Column(Date, nullable=True)
    # 휴가 끝일
    to_date = Column(Date, nullable=True)
    # 사유
    reason = Column(Text, nullable=True)
    # 상태(ALLOWED/REJECTED/WAITING)
    state = Column(String(128), nullable=True)
    # 신청일시
    request_date = Column(DateTime, nullable=True)
    # 처리일시
    proc_date = Column(DateTime, nullable=True)


# 건강 검진 확인 신청에 대한 모델
class Medical_checkup_request(db.Model):
    __tablename__ = 'tb_medical_checkup_request'
    __table_args__ = {'extend_existing': True}

    # 식별용id
    id = Column(Integer, primary_key=True)
    # 신청자id
    user_id = Column(Integer, ForeignKey('tb_user.id', ondelete='CASCADE'), nullable=True)
    # 외래키가 참조하는 모델로 'medical_checkup_request_set'으로 역참조가 가능
    user = db.relationship('User', backref=db.backref('medical_checkup_request_set'))
    # 올린 이미지가 저장된 주소
    img_addr = Column(String(128), nullable=True)


# 급여 명세서에 대한 모델
class Pay_statement(db.Model):
    __tablename__ = 'tb_pay_statement'
    __table_args__ = {'extend_existing': True}

    # 식별용id
    id = Column(Integer, primary_key=True)
    # 년월
    year_month = Column(String(128), nullable=True)
    # 파일 주소
    file_address = Column(String(128), nullable=True)