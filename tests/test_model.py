"""Test for Model class"""
from datetime import datetime
import pytest

from custom_components.teslafi.const import SHIFTER_STATES, TESLAFI_DATE_FORMAT, VIN_YEARS
from custom_components.teslafi.model import (
    TeslaFiVehicle,
    TeslaFiTirePressure,
)

def test_TeslaFiVehicle_constructor():
    vehicle = TeslaFiVehicle({})
    
    assert isinstance(vehicle, TeslaFiVehicle)
    
def test_TeslaFiVehicle_update_non_empty():
    """Test TeslaFiVehicle class"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555",
        "display_name": "Test Car",
        "odometer": 12345.67,
        "car_version": "2023.10.1"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.vin == "5YJSA1CG3DFP14555"
    assert vehicle.name == "Test Car"
    assert vehicle.odometer == 12345.67
    assert vehicle.firmware_version == "2023.10.1"

def test_TeslaFiVehicle_update_non_empty_with_empty_data():
    """Test TeslaFiVehicle class with empty data"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555",
        "display_name": "Test Car",
        "odometer": 12345.67,
        "car_version": "2023.10.1"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    # Update with empty data
    vehicle.update_non_empty({})
    
    assert vehicle.vin == "5YJSA1CG3DFP14555"
    assert vehicle.name == "Test Car"
    assert vehicle.odometer == 12345.67
    assert vehicle.firmware_version == "2023.10.1"
    
def test_TeslaFiVehicle_update_no_inital_data():
    """Test TeslaFiVehicle class with empty data"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555",
        "display_name": "Test Car",
        "odometer": 12345.67,
        "car_version": "2023.10.1"
    }
    
    vehicle = TeslaFiVehicle({})
    
    # Update with empty data
    vehicle.update_non_empty(vehicle_data)
    
    assert vehicle.vin == "5YJSA1CG3DFP14555"
    assert vehicle.name == "Test Car"
    assert vehicle.odometer == 12345.67
    assert vehicle.firmware_version == "2023.10.1"
    
def test_TeslaFiVehicle_id():
    """Test TeslaFiVehicle class id property"""
    vehicle_data = {
        "id": "123.324 324",
        "vin": "5YJSA1CG3DFP14555",
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.id == "123.324 324"

def test_TeslaFiVehicle_id_use_vin():
    """Test TeslaFiVehicle class id property"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555",
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.id == "5YJSA1CG3DFP14555"

def test_TeslaFiVehicle_vehicle_id():
    """Test TeslaFiVehicle class id property"""
    vehicle_data = {
        "vehicle_id": "FOO_VEHICLE_ID",
        "vin": "5YJSA1CG3DFP14555",
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.vehicle_id == "FOO_VEHICLE_ID"

def test_TeslaFiVehicle_vehicle_id_use_vin():
    """Test TeslaFiVehicle class id property"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.vehicle_id == "5YJSA1CG3DFP14555"

def test_TeslaFiVehicle_firmware_version():
    """Test TeslaFiVehicle class id property"""
    vehicle_data = {
        "car_version": "2025.2.9"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.firmware_version == "2025.2.9"

def test_TeslaFiVehicle_firmware_version_none():
    """Test TeslaFiVehicle class firmware_version property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.firmware_version is None

def test_TeslaFiVehicle_name():
    """Test TeslaFiVehicle class name property"""
    vehicle_data = {
        "display_name": "Model 3"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.name == "Model 3"

def test_TeslaFiVehicle_name_none():
    """Test TeslaFiVehicle class name property"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555",
        "display_name": None
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.name == "2013 modelS 4555"
    
def test_TeslaFiVehicle_last_remote_update():
    """Test TeslaFiVehicle class last_remote_update property"""
    vehicle_data = {
        "Date": "2023-10-01 12:00:00"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.last_remote_update == datetime.strptime("2023-10-01 12:00:00", TESLAFI_DATE_FORMAT)

def test_TeslaFiVehicle_last_remote_update_none():
    """Test TeslaFiVehicle class last_remote_update property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    assert vehicle.last_remote_update is None

def test_TeslaFiVehicle_last_remote_update_parse_error():
    """Test TeslaFiVehicle class last_remote_update property"""
    vehicle_data = {
        "Date": "XXXX-10-01 12:00:00"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    assert vehicle.last_remote_update is None

def test_TeslaFiVehicle_car_type():
    """Test TeslaFiVehicle class car_type property"""
    vehicle_data = {
        "car_type": "modelS"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.car_type == "modelS"

def test_TeslaFiVehicle_car_type_from_vin():
    """Test TeslaFiVehicle class car_type property"""
    vehicle_data = {
        "car_type": "modelS"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.car_type == "modelS"

def test_TeslaFiVehicle_car_type_none():
    """Test TeslaFiVehicle class car_type property"""
    vehicle_data = {
        "vin": None
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.car_type is None
    
def test_TeslaFiVehicle_vin():
    """Test TeslaFiVehicle class vin property"""
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.vin == "5YJSA1CG3DFP14555"
    
def test_TeslaFiVehicle_car_state():
    """Test TeslaFiVehicle class car_state property"""
    vehicle_data = {
        "carState": "Idling"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.car_state == "idling"

def test_TeslaFiVehicle_car_state_none():
    """Test TeslaFiVehicle class car_state property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.car_state is None
    
def test_TeslaFiVehicle_model_year():
    vehicle_data = {
        "vin": "5YJSA1CG3DFP14555"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.model_year == 2013

def test_TeslaFiVehicle_model_year_none():
    vehicle_data = {
        "vin": None
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.model_year is None

def test_TeslaFiVehicle_model_year_invalid():
    vehicle_data = {
        "vin": "5YJSA1CG3ÁFP14555" # Invalid character Á for year decoding
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.model_year is None
    
def test_TeslaFiVehicle_is_in_gear():
    vehicle_data = {
        "carState": "driving",
        "shift_state": "D"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_in_gear is True
    
def test_TeslaFiVehicle_shift_state():
    """Test TeslaFiVehicle class shift_state property"""
    vehicle_data = {
        "carState": "driving",
        "shift_state": "R"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.shift_state == "reverse"

def test_TeslaFiVehicle_shift_state_not_driving():
    """Test TeslaFiVehicle class shift_state property"""
    vehicle_data = {
        "carState": "sleeping",
        "shift_state": ""
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.shift_state == "park"

def test_TeslaFiVehicle_is_locked():
    """Test TeslaFiVehicle class is_locked property"""
    vehicle_data = {
        "locked": True
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_locked is True
    
def test_TeslaFiVehicle_is_sleeping():
    """Test TeslaFiVehicle class is_sleeping property"""
    vehicle_data = {
        "carState": "sleeping"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_sleeping is True
    
def test_TeslaFiVehicle_charging_state():
    """Test TeslaFiVehicle class charging_state property"""
    vehicle_data = {
        "charging_state": "Charging"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charging_state == "charging"

def test_TeslaFiVehicle_charging_state_none():
    """Test TeslaFiVehicle class charging_state property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charging_state is None