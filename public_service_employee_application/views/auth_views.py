from flask import Blueprint, request, render_template

from public_service_employee_application.forms import UserLoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'GET':
        return render_template('auth/login.html', form=form)