from abc import abstractmethod
from typing import Collection, Any

from django.db.models import Model
from django.shortcuts import render, redirect

from utils import TableReportGenerator, get_desktop_path
from utils.forms import DateRangeForm


class ReportViewMixin:
    session_start_date_name: str = 'start_date'
    session_end_date_name: str = 'end_date'

    def post(self, request, *args, **kwargs):
        form = DateRangeForm(request.POST)

        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            request.session[self.session_start_date_name] = str(start_date)
            request.session[self.session_end_date_name] = str(end_date)

            context = self.get_context_data(start_date=start_date, end_date=end_date)
        else:
            context = self.get_context_data()

        return render(request, self.template_name, context=context)


class GenerateReportMixin:
    session_start_date_name: str = None
    session_end_date_name: str = None
    redirect_name: str = None
    report_main_header: str = 'Отчет'
    model: Model = None
    margins: tuple = (0.5, 0.5, 0.3, 0.3)

    def post(self, request, *args, **kwargs):
        start_date = request.session.get(self.session_start_date_name)
        end_date = request.session.get(self.session_end_date_name)

        doc_name: str = (f'{self.model.__name__.lower()}-report-{start_date}'
                         f'-{end_date}.docx')
        record_set = self.get_record_set(start_date, end_date)
        rows_count: int = self.get_rows_count(record_set)
        headers: list = self.get_headers_list()

        report = TableReportGenerator(doc_name, rows_count, len(headers), headers, *self.margins)
        report.add_header(self.report_main_header, 1)
        report.add_paragraph(f'С: {start_date}')
        report.add_paragraph(f'По: {end_date}')

        self.fill_table(report, record_set)
        report.save(f'{get_desktop_path()}\\{doc_name}')
        return redirect(self.redirect_name)

    @staticmethod
    def fill_table(report: TableReportGenerator, record_set):
        report.fill_table(record_set)

    @staticmethod
    def get_rows_count(record_set) -> int:
        return len(record_set)

    @classmethod
    def get_headers_list(cls) -> list:
        fields = cls.model._meta.fields
        return [field.verbose_name for field in fields]

    @abstractmethod
    def get_record_set(self, start_date: str, end_date: str) -> Collection[Collection[Any]]:
        raise NotImplementedError("get_record_set() must be implemented")
