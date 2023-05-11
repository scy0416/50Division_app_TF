from waitress import serve
from public_service_employee_application import app
serve(app, host='0.0.0.0', port=5000, threads=100)