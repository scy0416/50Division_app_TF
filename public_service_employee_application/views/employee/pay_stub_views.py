from flask import Blueprint, render_template, g, request, jsonify, url_for, send_from_directory
import os
import win32com.client as win32
import pythoncom

from public_service_employee_application.views.auth_views import login_required_employee
from public_service_employee_application.models import User, Year


# 블루프린트 객체 생성
bp = Blueprint('employee_pay_stub', __name__, url_prefix='/employee/pay_stub')

# 이 블루프린트의 최초 진입점
@bp.route('/', methods=['GET'])
@login_required_employee
def index():
    return render_template('user/pay_stub/pay_stub.html')

# 년도 선택창을 반환
@bp.route('/year/select', methods=['GET'])
@login_required_employee
def get_select_year():
    years = Year.query.order_by(Year.year.asc()).all()
    return render_template('user/pay_stub/selectYear.html', years=years)

# 급여명세서 pdf로 생성
@bp.route('/detail', methods=['GET'])
@login_required_employee
def get_pay_stub():
    user = User.query.get_or_404(g.user.id)
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

    save_path = os.path.join('static', 'pay_stub', 'results', str(year) + '년' + month + ' ' + name + '.pdf')
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

# 엑셀 프로그램을 열고 지정한 경로의 엑셀 파일을 열고 반환하는 함수
def open_excel_file(file_path):
    pythoncom.CoInitialize()
    excel_app = win32.gencache.EnsureDispatch('Excel.Application')
    excel_Visible = False

    workbook = excel_app.Workbooks.Open(file_path)
    return excel_app, workbook

# pdf를 출력한 화면을 반환
@bp.route('/detail/<pdfname>', methods=['GET'])
@login_required_employee
def print_pdf(pdfname):
    pdfPath = url_for('employee_pay_stub.send_pdf', filename=pdfname)
    return render_template('user/pay_stub/print_pdf.html', pdfpath=pdfPath)

# pdf파일을 전달하는 엔드포인트
@bp.route('/pdf/<filename>', methods=['GET'])
@login_required_employee
def send_pdf(filename):
    return send_from_directory('static/pay_stub/results', filename)