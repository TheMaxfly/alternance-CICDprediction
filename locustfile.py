from locust import HttpUser, between, task


VALID_PAYLOAD = {
    "data": {
        "dep": "59",
        "lum": 1,
        "atm": 1,
        "catr": 3,
        "agg": 2,
        "int": 1,
        "circ": 2,
        "col": 3,
        "vma_bucket": "51-80",
        "catv_family_4": "voitures_utilitaires",
        "manv_mode": 1,
        "driver_age_bucket": "25-34",
        "choc_mode": 1,
        "driver_trajet_family": "trajet_1",
        "time_bucket": "morning_06_11",
    }
}

INVALID_PAYLOAD = {
    "data": {
        "dep": "59",
    }
}


class PredictionUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(4)
    def predict_valid(self) -> None:
        with self.client.post(
            "/predict",
            json=VALID_PAYLOAD,
            name="POST /predict valid",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Expected 200 for valid payload, got {response.status_code}"
                )

    @task(1)
    def predict_invalid(self) -> None:
        with self.client.post(
            "/predict",
            json=INVALID_PAYLOAD,
            name="POST /predict invalid",
            catch_response=True,
        ) as response:
            if response.status_code == 422:
                response.success()
            else:
                response.failure(
                    f"Expected 422 for invalid payload, got {response.status_code}"
                )
