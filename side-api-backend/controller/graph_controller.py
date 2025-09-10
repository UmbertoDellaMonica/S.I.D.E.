from configuration.database_configuration import driver

from fastapi import APIRouter, Depends
from services.database_service import get_devices

router = APIRouter()


def get_db_driver():
    from configuration.database_configuration import driver

    if driver is None:
        raise RuntimeError("Neo4j driver not initialized")
    return driver


@router.get("/api/devices")
def handle_get_device_controller(driver=Depends(get_db_driver)):
    return get_devices(driver=driver)
