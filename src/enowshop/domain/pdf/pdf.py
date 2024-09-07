from datetime import datetime
from fpdf import FPDF


class PDF(FPDF):
    def __init__(self):
        super().__init__()
    def header(self):
        self.set_font('Arial', '', 12)
        # Add image in left corner
        self.image('logo.png', 10, 12, 33)
        self.cell(0, 30, 'Relatorio', 0, 1, 'C')
        self.cell(0, 1, f'Data de geração: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'R')
        self.ln(10)