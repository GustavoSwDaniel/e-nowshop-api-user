

from enowshop.domain.pdf.pdf import PDF
from enowshop.endpoints.orders.repository import OrderItemsRepository, OrdersRepository
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import locale

from enowshop.domain.s3.service import S3Service
from enowshop.endpoints.report.repository import ReportsRepository




class ReportService:
    def __init__(self, pdf_service: PDF, orders_repository: OrdersRepository, 
                 order_items_repository: OrderItemsRepository, s3_service: S3Service,
                 report_repository: ReportsRepository) -> None:
        self.pdf_service = pdf_service
        self.ch = 10
        self.order_repository = orders_repository
        self.order_items_repository = order_items_repository
        self.s3_service = s3_service
        self.report_repository = report_repository
    
    async def calc_total(self, orders):
        total = 0
        for order in orders:
            total += order.total_amount
        return total / 100
    
    def calc_dots(self, title: str, value, special_caracter: str = None):
        total_text_width = self.pdf_service.get_string_width(f"{title}: ")
        total_width = self.pdf_service.get_string_width(f"{value}")
        if special_caracter:
            total_width += self.pdf_service.get_string_width(special_caracter)
        available_width = self.pdf_service.w - self.pdf_service.l_margin - self.pdf_service.r_margin
        dots = "." * int((available_width - total_text_width - total_width) / self.pdf_service.get_string_width("."))
        return dots
    

    async def teste(self, params: dict, requester: str):
        self.pdf_service.add_font('Arial', '', 'arial.ttf',  uni=True)
        if params.get('date_start'):
            params['date_start'] = datetime.strptime(params['date_start'], '%Y-%m-%d')
        if params.get('date_end'):
            params['date_end'] = datetime.strptime(params['date_end'], '%Y-%m-%d')

        
        self.pdf_service.set_title("Relatorio de transações")
        orders = await self.order_repository.get_orders_between_dates(params['date_start'], params['date_end'])
        orders_per_state = await self.order_repository.get_order_group_by_state(params['date_start'], params['date_end'])
        previous_start_date = params['date_start'] - timedelta(days=30)
        previous_end_date = params['date_end'] - timedelta(days=30)
        orders_in_previous_period = await self.order_repository.get_orders_between_dates(previous_start_date - timedelta(days=30), previous_end_date)
        orders_per_payment_method = await self.order_repository.get_order_group_by_payment_method(params['date_start'], params['date_end'])
        top_products = await self.order_items_repository.get_top_3_products_most_sold(params['date_start'], params['date_end'])
        total = await self.calc_total(orders)
        order_does_not_conclude = await self.order_repository.get_order_does_not_concluded_or_cancel(params['date_start'], params['date_end'])
        self.pdf_service.add_page()
        self.pdf_service.set_font('Arial', 'B', 24)
        self.pdf_service.cell(w=0, h=20, txt="Relatorio de transações", ln=1)
        self.pdf_service.set_font('Arial', '', 12)
        self.pdf_service.cell(w=30, h=self.ch, txt="Data de inicio: ", ln=1)
        self.pdf_service.cell(w=30, h=self.ch, txt=params['date_start'].strftime('%d/%m/%Y'), ln=1)
        self.pdf_service.cell(w=30, h=self.ch, txt="Data final: ", ln=1)
        self.pdf_service.cell(w=30, h=self.ch, txt=params['date_end'].strftime('%d/%m/%Y'), ln=1)
        self.pdf_service.cell(w=30, h=self.ch, txt="Author: ", ln=0)
        self.pdf_service.cell(w=30, h=self.ch, txt=requester, ln=1)
        self.pdf_service.ln(self.ch)

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        total = locale.currency(total, grouping=True)

        dots = self.calc_dots("Total de transações concluidas", len(orders))
        self.pdf_service.cell(w=30, h=self.ch, txt=f"Total de transações concluidas: {dots}{len(orders)}", ln=1)

        dots = self.calc_dots("Total do periodo", total)
        self.pdf_service.cell(w=30, h=self.ch, txt=f"Total do periodo: {dots}{total}", ln=2)

        dots = self.calc_dots("Total de pedido não concluidos", len(order_does_not_conclude))
        self.pdf_service.cell(w=30, h=self.ch, txt=f"Total de pedido não concluidos: {dots}{len(order_does_not_conclude)}", ln=3)

        porcentagem = len(order_does_not_conclude) / len(orders) * 100
        dots = self.calc_dots("Porcentagem de transções não concluidas", f'{porcentagem:.2f}', "%")
        self.pdf_service.cell(w=30, h=self.ch, txt=f"Porcentagem de transções não concluidas: {dots}{porcentagem:.2f}%", ln=4)

        porcentagem_concluidas = (len(orders) - len(order_does_not_conclude)) / len(orders) * 100
        dots = self.calc_dots("Porcentagem de transções concluidas", f'{porcentagem_concluidas:.2f}', "%")
        self.pdf_service.cell(w=30, h=self.ch, txt=f"Porcentagem de transções concluidas: {dots}{porcentagem_concluidas:.2f}%", ln=5)

        fig, ax = plt.subplots()

        ax.pie(orders_per_state.values(), labels=orders_per_state.keys())

        ax.set_title('Vendas por estado')

        plt.savefig('./example_chart.png', 
           transparent=False,  
           facecolor='white', 
           bbox_inches="tight")
        
        self.pdf_service.ln(self.ch)
        self.pdf_service.multi_cell(w=0, h=5, txt="teste")
        self.pdf_service.image('./example_chart.png', 
                                x = 10, y = None, w = 120, h = 0, type = 'PNG')
        
        self.pdf_service.ln(self.ch)
        fig, ax = plt.subplots()

        for payment_method, total in orders_per_payment_method.items():
            ax.bar(payment_method, total, label=payment_method)

        ax.set_title('Vendas por metodo de pagamento')
        ax.legend(title='Metodos de pagamento')

        plt.savefig('./payment_methods.png', 
           transparent=False,  
           facecolor='white', 
           bbox_inches="tight")
        
        self.pdf_service.ln(self.ch)
        self.pdf_service.image('./payment_methods.png', 
                                x = 10, y = None, w = 120, h = 0, type = 'PNG')
        

        self.pdf_service.ln(self.ch)
        fig, ax = plt.subplots()

        ax.bar(['Periodo anterior', 'Periodo atual'], 
               [len(orders_in_previous_period), len(orders)],
               label=['Periodo anterior', 'Periodo atual'])

        ax.set_title('Vendas por periodo')
        ax.legend(title='Metodos de pagamento')

        plt.savefig('./period.png', 
           transparent=False,  
           facecolor='white', 
           bbox_inches="tight")
        
        self.pdf_service.ln(self.ch)
        self.pdf_service.multi_cell(w=0, h=5, txt="teste")
        self.pdf_service.image('./period.png', 
                                x = 10, y = None, w = 120, h = 0, type = 'PNG')


        left_margin = self.pdf_service.l_margin
        right_margin = self.pdf_service.w - self.pdf_service.r_margin
        usable_width = right_margin - left_margin
        column_width = usable_width / 2

        
        self.pdf_service.ln(self.ch)
        self.pdf_service.set_font('Arial', 'B', 12)
        self.pdf_service.cell(w=column_width, h=20, txt="Produtos mais vendido", ln=1)
        self.pdf_service.set_font('Arial', 'B', 12)
        title = 'Produto' 
        self.pdf_service.cell(w=column_width, h=self.ch, txt=title, border=1, ln=0, align='C') 
        title = 'Numero de produtos vendidos'
        self.pdf_service.cell(w=column_width, h=self.ch, txt=title, border=1, ln=1, align='C')
        
        
        for product, total in top_products.items(): 
            self.pdf_service.set_font('Arial', '', 12)
            if self.pdf_service.get_string_width(product) > column_width:
                product = product[:38] + '...'
            self.pdf_service.cell(w=column_width, h=8, 
                    txt=product, 
                    border=1, ln=0, align='C') 
            self.pdf_service.cell(w=column_width, h=8, 
                    txt=str(total), 
                    border=1, ln=1, align='C')
        conteudo_pdf = self.pdf_service.output(dest='S').encode('latin-1')
        
        url = self.s3_service.upload_report(conteudo_pdf)
        data = {
            "url": url,
            "user_id": 1,
        }
        await self.report_repository.create(data)
        return conteudo_pdf

    async def get_reports(self):
        return await self.report_repository.get_all()
