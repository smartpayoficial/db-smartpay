from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse

from app.schemas.analytics import AnalyticsResponse
from app.services.analytics import analytics_service

router = APIRouter()


@router.get(
    "/date-range",
    response_class=JSONResponse,
    response_model=AnalyticsResponse,
    status_code=200,
)
async def get_analytics_by_date_range(
    start_date: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha final (YYYY-MM-DD). Si no se proporciona, se usa la fecha actual"),
    store_id: Optional[UUID] = Query(None, description="ID de la tienda para filtrar los datos"),
):
    """
    Obtiene estadísticas diarias por rango de fechas.
    
    Retorna:
    - totales para el rango completo
    - desglose diario con:
      - customers: conteo de clientes creados cada día
      - devices: conteo de dispositivos creados cada día
      - payments: valor total de pagos cada día
      - vendors: conteo de vendedores creados cada día
    
    Si solo se proporciona start_date, obtiene datos desde esa fecha hasta hoy.
    """
    analytics_data = await analytics_service.get_analytics_by_date_range(
        start_date=start_date,
        end_date=end_date,
        store_id=store_id
    )
    
    return analytics_data


@router.get(
    "/excel",
    response_class=StreamingResponse,
    status_code=200,
)
async def download_analytics_excel(
    start_date: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha final (YYYY-MM-DD). Si no se proporciona, se usa la fecha actual"),
    store_id: Optional[UUID] = Query(None, description="ID de la tienda para filtrar los datos"),
):
    """
    Genera y descarga un archivo Excel con el detalle completo de las estadísticas.
    
    Incluye:
    - Resumen de totales
    - Detalle de clientes creados en el rango
    - Detalle de vendedores creados en el rango
    - Detalle de dispositivos creados en el rango
    - Detalle de pagos realizados en el rango
    
    Si solo se proporciona start_date, obtiene datos desde esa fecha hasta hoy.
    """
    excel_buffer = await analytics_service.generate_analytics_excel(
        start_date=start_date,
        end_date=end_date,
        store_id=store_id
    )
    
    # Generate filename with date range
    end_date_str = end_date.strftime('%Y-%m-%d') if end_date else date.today().strftime('%Y-%m-%d')
    filename = f"analytics_report_{start_date.strftime('%Y-%m-%d')}_to_{end_date_str}.xlsx"
    
    return StreamingResponse(
        iter([excel_buffer.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
