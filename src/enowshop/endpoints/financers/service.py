



from datetime import datetime
from enowshop.endpoints.financers.repository import FinancersRepository
from enowshop.endpoints.paginate import paginate
import matplotlib.pyplot as plt

import locale

from enowshop.domain.pdf.pdf import PDF

class FinancersService:
    def __init__(self, financers_repository: FinancersRepository, pdf_service: PDF):
        self.financers_repository = financers_repository
        self.pdf_service = pdf_service
        self.ch = 10

    def create_financer(self, financer_data):
        return self.financers_repository.create(financer_data)
    
    async def get_financers(self, params: dict):
        results, total =  await self.financers_repository.get_financers(params)
        return paginate(results, params.get('offset'), total)

    def get_financers_by_type(self, type: str):
        querys = {
            'all': self.financers_repository.get_financers_between_dates,
            'receita': self.financers_repository.get_financers_revenue,
            'gastos': self.financers_repository.get_financers_expenses
        }
        return querys.get(type)
    
    async def generate_cash(self, params: dict):
        self.pdf_service.add_font('Arial', '', 'arial.ttf',  uni=True)
        self.pdf_service.set_title("Relatorio de transações")

        if params.get('start_date'):
            params['start_date'] = datetime.strptime(params['start_date'], '%Y-%m-%d')
        if params.get('end_date'):
            params['end_date'] = datetime.strptime(params['end_date'], '%Y-%m-%d')

        financers = await self.get_financers_by_type(params.get('type'))(params)
        total = 0
        for financer in financers:
            total += financer.value

        left_margin = self.pdf_service.l_margin
        right_margin = self.pdf_service.w - self.pdf_service.r_margin
        usable_width = right_margin - left_margin
        column_width = usable_width / 2

        self.pdf_service.set_title("Relatorio de fluxo")
        self.pdf_service.add_page()

        self.pdf_service.ln(self.ch)
        self.pdf_service.set_font('Arial', 'B', 12)
        self.pdf_service.cell(w=column_width, h=20, txt="Relatorio de fluxo", ln=1)
        self.pdf_service.set_font('Arial', 'B', 12)
        
        
        for financer in financers: 
            self.pdf_service.set_font('Arial', '', 12)
            self.pdf_service.set_text_color(0, 0, 0)
            if self.pdf_service.get_string_width(financer.name) > column_width:
                setattr(financer, 'name', financer.name[:38] + '...')
            self.pdf_service.cell(w=column_width, h=8, 
                    txt=financer.name, 
                    border=1, ln=0, align='C') 
            if financer.type in ['gasto', 'despesa']:
                self.pdf_service.set_text_color(255, 0, 0)
                self.pdf_service.cell(w=column_width, h=8, 
                        txt=f'-{str(financer.value)}', 
                        border=1, ln=1, align='C',)
                continue
            self.pdf_service.set_text_color(0, 0, 255)
            self.pdf_service.cell(w=column_width, h=8, 
                        txt=str(financer.value), 
                        border=1, ln=1, align='C')

        conteudo_pdf = self.pdf_service.output(dest='S').encode('latin-1')
        return conteudo_pdf