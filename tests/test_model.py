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

def test_TeslaFiVehicle_shift_state_None():
    """Test TeslaFiVehicle class shift_state property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.shift_state is None

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
    
def test_TeslaFiVehicle_charge_session_number():
    """Test TeslaFiVehicle class charge_session_number property"""
    vehicle_data = {
        "chargeNumber": 123
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charge_session_number == 123

def test_TeslaFiVehicle_charge_session_number_zero():
    """Test TeslaFiVehicle class charge_session_number property"""
    vehicle_data = {
        "chargeNumber": 0
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charge_session_number is None
    
def test_TeslaFiVehicle_is_plugged_in():
    """Test TeslaFiVehicle class is_plugged_in property"""
    vehicle_data = {
        "charging_state": "Charging"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_plugged_in is True

def test_TeslaFiVehicle_is_plugged_in_False():
    """Test TeslaFiVehicle class is_plugged_in property"""
    vehicle_data = {
        "charging_state": "Disconnected"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_plugged_in is False
    
def test_TeslaFiVehicle_is_charging():
    """Test TeslaFiVehicle class is_charging property"""
    vehicle_data = {
        "charging_state": "Charging"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_charging is True

def test_TeslaFiVehicle_is_charging_False():
    """Test TeslaFiVehicle class is_charging property"""
    vehicle_data = {
        "charging_state": "Stopped"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_charging is False
    
def test_TeslaFiVehicle_is_fast_charger():
    """Test TeslaFiVehicle class is_fast_charger property"""
    vehicle_data = {
        "charging_state": "Charging",
        "fast_charger_present": True
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_fast_charger is True

def test_TeslaFiVehicle_is_fast_charger_default_False():
    """Test TeslaFiVehicle class is_fast_charger property"""
    vehicle_data = {
        "charging_state": "Charging",
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_fast_charger is False
    
def test_TeslaFiVehicle_charger_current():
    """Test TeslaFiVehicle class charger_current property"""
    vehicle_data = {
        "charger_actual_current": 32
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_current == 32

def test_TeslaFiVehicle_charger_current_none():
    """Test TeslaFiVehicle class charger_current property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_current is None

def test_TeslaFiVehicle_charger_current_fast():
    """Test TeslaFiVehicle class charger_current property"""
    vehicle_data = {
        "charging_state": "Charging",
        "fast_charger_present": True,
        "charger_power": 200,
        "charger_voltage": 100,
        
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_current == 2

def test_TeslaFiVehicle_charger_voltage():
    """Test TeslaFiVehicle class charger_voltage property"""
    vehicle_data = {
        "charger_voltage": 240
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_voltage == 240
    
def test_TeslaFiVehicle_charger_level_1():
    """Test TeslaFiVehicle class charger_level property"""
    vehicle_data = {
        "charging_state": "Charging",
        "charger_voltage": 120
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_level == "level-1"

def test_TeslaFiVehicle_charger_level_2():
    """Test TeslaFiVehicle class charger_level property"""
    vehicle_data = {
        "charging_state": "Charging",
        "charger_voltage": 240
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_level == "level-2"

def test_TeslaFiVehicle_charger_level_3():
    """Test TeslaFiVehicle class charger_level property"""
    vehicle_data = {
        "charging_state": "Charging",
        "charger_voltage": 240,
        "fast_charger_present": True
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_level == "level-3"

def test_TeslaFiVehicle_charger_level_none():
    """Test TeslaFiVehicle class charger_level property"""
    vehicle_data = {
        "charging_state": "Charging",
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_level is None

def test_TeslaFiVehicle_charger_level_none_unplugged():
    """Test TeslaFiVehicle class charger_level property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.charger_level is None
    
def test_TeslaFiVehicle_is_defrosting_front():
    """Test TeslaFiVehicle class is_defrosting property"""
    vehicle_data = {
        "is_front_defroster_on": "1"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_defrosting is True

def test_TeslaFiVehicle_is_defrosting_rear():
    """Test TeslaFiVehicle class is_defrosting property"""
    vehicle_data = {
        "is_front_defroster_on": "1"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_defrosting is True

def test_TeslaFiVehicle_is_defrosting_mode():
    """Test TeslaFiVehicle class is_defrosting property"""
    vehicle_data = {
        "defrost_mode": "1"
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_defrosting is True

def test_TeslaFiVehicle_is_defrosting_mode_False():
    """Test TeslaFiVehicle class is_defrosting property"""
    vehicle_data = {
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert vehicle.is_defrosting is False

def test_TeslaFiVehicle_tpms():
    """Test TeslaFiVehicle class tpms property"""
    vehicle_data = {
        "tpms_front_left": "43.0",
        "tpms_front_right": "42.5",
        "tpms_rear_left": "41.5",
        "tpms_rear_right": "44.0",
        "pressure": "psi",
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert isinstance(vehicle.tpms, TeslaFiTirePressure)
    assert vehicle.tpms.front_left == 43.0
    assert vehicle.tpms.front_right == 42.5
    assert vehicle.tpms.rear_left == 41.5
    assert vehicle.tpms.rear_right == 44.0
    assert vehicle.tpms.unit == "psi"

def test_TeslaFiVehicle_tpms_none():
    """Test TeslaFiVehicle class tpms property"""
    vehicle_data = {
        "tpms_front_left": None,
        "tpms_front_right": None,
        "tpms_rear_left": None,
        "tpms_rear_right": None
    }
    
    vehicle = TeslaFiVehicle(vehicle_data)
    
    assert isinstance(vehicle.tpms, TeslaFiTirePressure)
    assert vehicle.tpms.front_left is None
    assert vehicle.tpms.front_right is None
    assert vehicle.tpms.rear_left is None
    assert vehicle.tpms.rear_right is None
    assert vehicle.tpms.unit == "psi"

def test_TeslaFiTirePressure_constructor():
    """Test TeslaFiTirePressure class"""
    
    tire_pressure = TeslaFiTirePressure(
        front_left=43.0,
        front_right=42.5,
        rear_left=41.5,
        rear_right=44.0,
        unit="psi",
    )
    
    assert isinstance(tire_pressure, TeslaFiTirePressure)
    
def test_TeslaFiTirePressure_convert_unit():
    """Test TeslaFiTirePressure class convert_unit method"""
    
    assert TeslaFiTirePressure.convert_unit("psi") == "psi"