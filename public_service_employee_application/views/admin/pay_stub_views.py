from flask import Blueprint, request, g, render_template, jsonify, url_for, send_from_directory
from sqlalchemy import and_, func
import os
import win32com.client as win32
import pythoncom

from public_service_employee_application.views.auth_views import login_required_admin
from public_service_employee_application.models import User, Year
from public_service_employee_application import db

# 블루프린트 객체 생성
bp = Blueprint('admin_pay_stub', __name__, url_prefix='/admin/pay_stub')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_admin
def index():
    # 검색 및 페이징
    page = request.args.get('page', type=int, default=1)
    q = request.args.get('q', type=str, default='')

    # 검색 처리
    user_list = User.query.filter(and_(User.role == 'USER', User.name.contains(q)))
    user_list = user_list.paginate(page=page, per_page=5)

    return render_template('admin/pay_stub/pay_stub.html', user_list=user_list, page=page, q=q)

# 년도 추가 다이어로그를 반환
@bp.route('/year/dialog/addYear', methods=['GET'])
@login_required_admin
def get_dialog_addYear():
    #print(render_template('admin/pay_stub/addYear.html'))
    return render_template('admin/pay_stub/addYear.html')

# 새 년도 정보를 추가
@bp.route('/year/add', methods=['POST'])
@login_required_admin
def addYear():
    data = request.get_json()
    year = data.get('year')
    year = int(year)

    result = []
    yearData = Year.query.filter(Year.year == year).first()
    if yearData == None:
        result.append({
            'isOverlap': False
        })
        newYear = Year(year=year)
        db.session.add(newYear)
        db.session.commit()
    elif yearData != None:
        result.append({
            'isOverlap': True
        })

    return jsonify(result)

# 년도 정보를 삭제
@bp.route('/year/<id>/delete', methods=['POST'])
@login_required_admin
def deleteYear(id):
    result = []
    if db.session.query(func.count(Year.id)).scalar() <= 1:
        result.append({
            'isOnly': True
        })
    else:
        result.append({
            'isOnly': False
        })
        year = Year.query.get_or_404(id)
        db.session.delete(year)
        db.session.commit()
    return jsonify(result)

# 년도 선택창을 반환
@bp.route('/year/select', methods=['GET'])
@login_required_admin
def get_select_year():
    years = Year.query.order_by(Year.year.asc()).all()
    return render_template('admin/pay_stub/selectYear.html', years=years)

# 유저 목록
@bp.route('/employee', methods=['GET'])
@login_required_admin
def get_user_list():
    # 검색 및 페이징 처리
    q = request.args.get('q', type=str, default='')
    page = request.args.get('page', type=int, default=1)

    user_list = User.query.filter(and_(User.role == 'USER', User.name.contains(q)))
    user_list = user_list.paginate(page=page, per_page=5)

    return render_template('admin/pay_stub/user_list.html', user_list=user_list, q=q, page=page)

# 파일 입력 다이어로그
@bp.route('/file/upload', methods=['GET'])
@login_required_admin
def get_file_upload():
    return render_template('admin/pay_stub/file_upload.html')


# 년도에 대한 파일 업로드
@bp.route('/file/upload/<int:year_id>', methods=['POST'])
@login_required_admin
def upload_file(year_id):
    year = Year.query.get_or_404(year_id)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        file_path = os.path.join('static', 'pay_stub', str(year.year) + '.xlsx')
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

# 급여명세서 pdf로 생성
@bp.route('/<int:user_id>/detail', methods=['GET'])
@login_required_admin
def get_pay_stub(user_id):
    user = User.query.get_or_404(user_id)
    name = user.name
    year_id = request.args.get('year_id', default=2023)
    year = Year.query.get_or_404(year_id).year
    month = request.args.get('month', default=1)

    isEmployeeExist = True
    isMonthDataExist = True

    file_path = os.path.join('static', 'pay_stub', str(year) + '.xlsx')
    excel_app, workbook = open_excel_file(os.path.abspath(file_path))

    num = -1
    info = workbook.Worksheets('인사기본정보')
    i = 5
    while True:
        if info.Cells(i, 3).Value == name:
            num = info.Cells(i, 2).Value
            break
        elif info.Cells(i, 3).Value is None:
            workbook.Close(SaveChanges=False)
            excel_app.Quit()
            isEmployeeExist = False
            response = {
                'isEmployeeExist': isEmployeeExist,
                'isMonthDataExist': isMonthDataExist
            }
            return jsonify(response)
        i += 1

    month = '0' + str(month)
    month = month[-2:] + '월'
    month_sheet = workbook.Worksheets(month)
    if month_sheet.Cells(num + 5, 20).Value == 0:
        isMonthDataExist = False
        workbook.Close(SaveChanges=False)
        excel_app.Quit()
        response = {
            'isEmployeeExist': isEmployeeExist,
            'isMonthDataExist': isMonthDataExist
        }
        return jsonify(response)

    pay_stub_sheet = workbook.Worksheets('급여명세서')
    pay_stub_sheet.Cells(7, 25).Value = num

    pay_stub_sheet.Cells(5, 8).Value = str(year) + '년'
    pay_stub_sheet.Cells(5, 13).Value = month

    save_path = os.path.join('static', 'pay_stub', 'results', str(year) + "년" + month + ' ' + name + '.pdf')
    save_path = os.path.abspath(save_path)
    pay_stub_sheet.ExportAsFixedFormat(0, save_path)

    workbook.Close(SaveChanges=False)
    excel_app.Quit()

    pdfName = str(year) + '년' + month + ' ' + name + '.pdf'
    response = {
        'isEmployeeExist': isEmployeeExist,
        'isMonthDataExist': isMonthDataExist,
        'pdfName': pdfName
    }
    return jsonify(response)

#엑셀 프로그램을 열고 지정한 경로의 엑셀 파일을 열고 반환하는 함수
def open_excel_file(file_path):
    pythoncom.CoInitialize()
    excel_app = win32.gencache.EnsureDispatch('Excel.Application')
    excel_app.Visible = False

    workbook = excel_app.Workbooks.Open(file_path)
    return excel_app, workbook

# pdf를 출력한 화면을 반환
@bp.route('/pdf/detail/<pdfname>', methods=['GET'])
@login_required_admin
def print_pdf(pdfname):
    pdfPath = url_for('admin_pay_stub.send_pdf', filename=pdfname)
    return render_template('admin/pay_stub/print_pdf.html', pdfpath=pdfPath)

# pdf파일을 전달하는 엔드포인트
@bp.route('/pdf/<filename>', methods=['GET'])
@login_required_admin
def send_pdf(filename):
    return send_from_directory('static/pay_stub/results', filename)