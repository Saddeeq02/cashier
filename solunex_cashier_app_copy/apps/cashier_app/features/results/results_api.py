# apps\cashier_app\features\results\results_api.py

from shared.api.client import client


def list_results(patient_id: int, role: str = "cashier"):
    return client.get(
        "/api/results",
        params={"patient_id": patient_id},
        headers={"x-role": role}
    )


def release_result(result_id: int):
    return client.patch(
        f"/api/results/{result_id}/status",
        json={"status": "released"},
        headers={"x-role": "admin"}
    )


def get_result(result_id: int):
    return client.get(
        f"/api/results/{result_id}",
        headers={"x-role": "cashier"}  # or "admin" depending on your policy
    )