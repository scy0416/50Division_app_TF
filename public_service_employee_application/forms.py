from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo

# 로그인 창을 위한 입력 폼 클래스
class UserLoginForm(FlaskForm):
    # id 확인
    id = StringField('사용자이름', validators=[
        DataRequired(),Length(min=3, max=25)
    ])
    # 비밀번호 확인
    password =PasswordField('비밀번호', validators=[DataRequired()])

# 관리자 추가를 위한 입력 폼 클래스
class AddAdmin(FlaskForm):
    # id 확인
    id = StringField('id', validators=[
        DataRequired(), Length(min=3, max=25)
    ])
    # 비밀번호 확인
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다.')
    ])
    # 비밀번호 일치하는지 확인
    password2 = PasswordField('비밀번호', validators=[DataRequired()])

# 공무직원 추가를 위한 입력 폼 클래스
class AddEmployee(FlaskForm):
    # 이름
    name = StringField('이름', validators=[
        DataRequired(), Length(min=3, max=50)
    ])
    # 부대명
    unit_name = StringField('부대명', validators=[
        DataRequired(), Length(min=3, max=50)
    ])
    # 직책
    position = StringField('직책', validators=[
        DataRequired(), Length(min=3, max=50)
    ])
    # 생년월일
    birth_date = DateField('생년월일', validators=[DataRequired()])
    # 채용일
    hire_date = DateField('채용일', validators=[DataRequired()])
    # 퇴직일
    retirement_date = DateField('퇴직일', validators=[DataRequired()])
    # 고용형태
    employment_type = SelectField('고용형태', choices=[('공무직', 'PUBLIC_SERVICE'), ('기간제', 'FIXED_TERM'), ('단기간', 'SHORT_TERM')], validators=[DataRequired()])
    # 비고
    bigo = StringField('비고')