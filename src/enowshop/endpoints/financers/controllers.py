

from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, Request, Response
from dependency_injector.wiring import inject
from dependency_injector.wiring import inject, Provide
from enowshop.infrastructure.containers import Container

from fpdf import FPDF

from enowshop.endpoints.report.schema import ReportSchema
from enowshop.endpoints.financers.service import FinancersService
from enowshop.endpoints.financers.schemas import CostRegister, PaginateCostsSchema

router = APIRouter(tags=["Finacenrio"])

@router.post("/financer")
@inject
async def create_financer(request: Request, data: CostRegister,
                     finace_service: FinancersService = Depends(Provide[Container.finace_service])):
    return await finace_service.create_financer(data.dict())
    

@router.get("/financers", response_model=PaginateCostsSchema)
@inject
async def get_reports(request: Request, limit: int = 12, offset: int = 0, type : Union[str, None] = None, start_date: Union[str, None] = None, end_date: Union[str, None] = None,
                     finace_service: FinancersService = Depends(Provide[Container.finace_service])):
    params = {
        'limit': limit,
        'offset': offset,
        'type': type,
        'start_date': start_date,
        'end_date': end_date
    }
    finace =  await finace_service.get_financers(params=params)
    return finace


@router.get("/financers/flow")
@inject
async def get_reports_cash_flow(request: Request, start_date: Union[str, None] = None, end_date: Union[str, None] = None, type: Union[str] = 'all',
                     finace_service: FinancersService = Depends(Provide[Container.finace_service])):
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'type': type
    }
    conteudo_pdf =  await finace_service.generate_cash(params=params)
    headers = {
            "Content-Disposition": "attachment; filename=relatorio.pdf",
            "Content-Type": "application/pdf",
        }
    return Response(content=conteudo_pdf, headers=headers)


@router.get("/financers/revenue")
@inject
async def get_reports_cash_flow(request: Request, start_date: Union[str, None] = None, end_date: Union[str, None] = None,
                     finace_service: FinancersService = Depends(Provide[Container.finace_service])):
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'type': 'gastos'
    }
    conteudo_pdf =  await finace_service.generate_cash(params=params)
    headers = {
            "Content-Disposition": "attachment; filename=relatorio.pdf",
            "Content-Type": "application/pdf",
        }
    return Response(content=conteudo_pdf, headers=headers)


@router.get("/financers/cost")
@inject
async def get_reports_cash_revenue(request: Request, start_date: Union[str, None] = None, end_date: Union[str, None] = None,
                     finace_service: FinancersService = Depends(Provide[Container.finace_service])):
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'type': 'receita'
    }
    conteudo_pdf =  await finace_service.generate_cash(params=params)
    headers = {
            "Content-Disposition": "attachment; filename=relatorio.pdf",
            "Content-Type": "application/pdf",
        }
    return Response(content=conteudo_pdf, headers=headers)




def configure(app: FastAPI):
    app.include_router(router)

