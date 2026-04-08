from shared.api.client import APIClient
from apps.cashier_app.app_state import state
import time

api_client = APIClient()


def get_verified_bookings():
    return api_client.get(
        "/api/payments/verified-bookings",
        params={"_t": time.time()}   # cache buster
    )


def convert_patient(booking_id, patient_name):
    return api_client.post(
        f"/api/bookings/{booking_id}/convert",
        params={
            "patient_name": patient_name,
            "branch_id": state.branch_id,
            "cashier_name": state.username,
        }
    )


def get_booking_patients(booking_id):
    return api_client.get(f"/api/bookings/{booking_id}/patients")