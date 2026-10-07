from fastapi import APIRouter, HTTPException, Path, Query, Request

from app.models.meter import (
    ConsumptionResponse,
    LocationResponse,
    Meter,
    MeterList,
)
from app.services.meter_service import MeterService


router = APIRouter(prefix="/api/v1")


def get_service(request: Request) -> MeterService:
    return MeterService(request.app.state.portal_client)


@router.get(
    "/meters",
    response_model=MeterList,
)
def search_meters(
    request: Request,
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1),
) -> MeterList:
    service = get_service(request)

    try:
        return service.search_meters(
            query=search,
            page=page,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve meters from upstream portal",
        ) from exc


@router.get(
    "/meters/{meter_id}",
    response_model=Meter,
)
def get_meter(
    request: Request,
    meter_id: str = Path(
        ...,
        min_length=1,
        max_length=50,
    ),
) -> Meter:
    service = get_service(request)

    try:
        return service.get_meter(meter_id)
    except LookupError:
        raise HTTPException(
            status_code=404,
            detail=f"Meter '{meter_id}' not found",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve meter from upstream portal",
        ) from exc


@router.get(
    "/meters/{meter_id}/consumption",
    response_model=ConsumptionResponse,
)
def get_consumption(
    request: Request,
    meter_id: str = Path(
        ...,
        min_length=1,
        max_length=50,
    ),
) -> ConsumptionResponse:
    service = get_service(request)

    try:
        return service.get_consumption(meter_id)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve consumption data from upstream portal",
        ) from exc


@router.get(
    "/meters/{meter_id}/location",
    response_model=LocationResponse,
)
def get_location(
    request: Request,
    meter_id: str = Path(
        ...,
        min_length=1,
        max_length=50,
    ),
) -> LocationResponse:
    service = get_service(request)

    try:
        return service.get_location(meter_id)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve location data from upstream portal",
        ) from exc