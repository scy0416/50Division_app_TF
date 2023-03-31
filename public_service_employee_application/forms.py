from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

# 로그인 창을 위한 입력 폼 클래스
class UserLoginForm(FlaskForm):
    # id 확인
    id = StringField('사용자이름', validators=[
        DataRequired(),Length(min=3, max=25)
    ])
    # 비밀번호 확인
    password =PasswordField('비밀번호', validators=[DataRequired()])