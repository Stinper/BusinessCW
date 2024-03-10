from django.urls import path

from employees.views import (EmployeesView, CreateEmployeeView, UpdateEmployeeView, DeleteEmployeeView,
                             ListSalaryView, UpdateSalaryView, IssueSalaryView)

app_name = 'employees'

urlpatterns = [
    path('', EmployeesView.as_view(), name='index'),
    path('create/', CreateEmployeeView.as_view(), name='create'),
    path('update/<int:pk>/', UpdateEmployeeView.as_view(), name='update'),
    path('delete/<int:pk>/', DeleteEmployeeView.as_view(), name='delete'),
    path('salary/', ListSalaryView.as_view(), name='salary-index'),
    path('salary/update/<int:pk>', UpdateSalaryView.as_view(), name='salary-update'),
    path('salary/issue-all', IssueSalaryView.as_view(), name='salary-issue')
]
