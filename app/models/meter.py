from pydantic import BaseModel


class Meter(BaseModel):
    meter_id: str
    serial_number: str
    make: str
    phase_type: str
    installation_status: str
    distribution_transformer: str


class MeterList(BaseModel):
    data: list[Meter]
    total: int
    page: int
    page_size: int


class EnergyReading(BaseModel):
    timestamp: str
    kwh: float
    kvah: float
    voltage_r: float


class ConsumptionResponse(BaseModel):
    meter_id: str
    readings: list[EnergyReading]


class LocationResponse(BaseModel):
    meter_id: str
    latitude: float
    longitude: float