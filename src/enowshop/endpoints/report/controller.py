

from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, Request, Response
from dependency_injector.wiring import inject
from dependency_injector.wiring import inject, Provide
from enowshop.infrastructure.containers import Container

from fpdf import FPDF

from enowshop.endpoints.report.schema import ReportSchema

router = APIRouter(tags=["Report"])

@router.get("/report")
@inject
async def get_report(request: Request, start_date: Union[str, None] = None, end_date: Union[str, None] = None,
                     report_service = Depends(Provide[Container.report_service])):
    params = request.query_params
    params = {
        'date_start': start_date,
        'date_end': end_date,
    }
    
    
    conteudo_pdf = await report_service.teste(params, requester='Gustavo')
    headers = {
        "Content-Disposition": "attachment; filename=relatorio.pdf",
        "Content-Type": "application/pdf",
    }
    return Response(content=conteudo_pdf, headers=headers)

@router.get("/reports", response_model=List[ReportSchema])
@inject
async def get_reports(request: Request, report_service = Depends(Provide[Container.report_service])):
    reports = await report_service.get_reports()
    return reports


def configure(app: FastAPI):
    app.include_router(router)

