from datetime import datetime

from app.models.meter import (
    ConsumptionResponse,
    EnergyReading,
    LocationResponse,
    Meter,
    MeterList,
)
from app.portal.client import PortalClient


class MeterService:
    def __init__(self, portal_client: PortalClient) -> None:
        self.portal_client = portal_client

    def search_meters(
        self,
        query: str = "",
        page: int = 1,
    ) -> MeterList:
        result = self.portal_client.search_meters(
            query=query,
            page=page,
        )

        meters = [
            Meter(
                meter_id=item["meterId"],
                serial_number=item["serialNo"],
                make=item["make"],
                phase_type=item["phaseType"],
                installation_status=item["installStatus"],
                distribution_transformer=item["dtCode"],
            )
            for item in result["data"]
        ]

        return MeterList(
            data=meters,
            total=result["total"],
            page=result["page"],
            page_size=result["pageSize"],
        )

    def get_meter(self, meter_id: str) -> Meter:
        result = self.portal_client.search_meters(
            query=meter_id,
            page=1,
        )

        for item in result["data"]:
            if item["meterId"] == meter_id:
                return Meter(
                    meter_id=item["meterId"],
                    serial_number=item["serialNo"],
                    make=item["make"],
                    phase_type=item["phaseType"],
                    installation_status=item["installStatus"],
                    distribution_transformer=item["dtCode"],
                )

        raise LookupError(f"Meter '{meter_id}' not found")

    def get_consumption(
        self,
        meter_id: str,
    ) -> ConsumptionResponse:
        result = self.portal_client.get_energy(meter_id)

        readings = []

        for item in result["data"]:
            readings.append(
                EnergyReading(
                    timestamp=self._parse_timestamp(item["timestamp"]),
                    kwh=float(item["kwh"]),
                    kvah=float(item["kvah"]),
                    voltage_r=float(item["voltR"]),
                )
            )

        return ConsumptionResponse(
            meter_id=meter_id,
            readings=readings,
        )

    def get_location(
        self,
        meter_id: str,
    ) -> LocationResponse:
        result = self.portal_client.get_geo(meter_id)

        return LocationResponse(
            meter_id=meter_id,
            latitude=float(result["data"]["latitude"]),
            longitude=float(result["data"]["longitude"]),
        )

    @staticmethod
    def _parse_timestamp(value: str) -> str:
        parsed = datetime.strptime(
            value,
            "%d/%m/%Y %H:%M",
        )

        return parsed.isoformat()