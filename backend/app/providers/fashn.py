import base64
import time
import httpx

from app.config import settings
from app.providers.base import TryOnProvider

POLL_INTERVAL = 2.0
POLL_TIMEOUT = 120.0


class FashnProvider(TryOnProvider):
    name = "fashn-tryon-max"

    def generate(self, person_image_path, garment_image_url, category):
        if not settings.fashn_api_key:
            raise RuntimeError("FASHN API key is not configured. Set FASHN_API_KEY in backend/.env")

        with open(person_image_path, "rb") as f:
            person_b64 = base64.b64encode(f.read()).decode("utf-8")
        person_data_uri = f"data:image/jpeg;base64,{person_b64}"

        headers = {
            "Authorization": f"Bearer {settings.fashn_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model_name": "tryon-max",
            "inputs": {
                "product_image": garment_image_url,
                "model_image": person_data_uri,
                "return_base64": True,
                "output_format": "jpeg",
                "generation_mode": "fast",
                "resolution": "1k",
            },
        }

        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{settings.fashn_api_url}/v1/run", headers=headers, json=body)

            if resp.status_code in (401, 403):
                raise RuntimeError("The FASHN API key is invalid or has no credits.")
            if not resp.status_code.ok if hasattr(resp.status_code, "ok") else resp.status_code < 200 or resp.status_code >= 300:
                try:
                    err = resp.json()
                    raise RuntimeError(err.get("message", f"FASHN error {resp.status_code}"))
                except (ValueError, KeyError):
                    raise RuntimeError(f"FASHN returned status {resp.status_code}")

            run_data = resp.json()
            if run_data.get("error"):
                raise RuntimeError(run_data["error"]["message"])

            prediction_id = run_data["id"]

            deadline = time.time() + POLL_TIMEOUT
            while time.time() < deadline:
                time.sleep(POLL_INTERVAL)
                status_resp = client.get(
                    f"{settings.fashn_api_url}/v1/status/{prediction_id}",
                    headers=headers,
                )
                if not status_resp.status_code < 400:
                    raise RuntimeError("FASHN status check failed.")

                status_data = status_resp.json()

                if status_data["status"] == "completed":
                    output = status_data.get("output")
                    if output and len(output) > 0 and output[0]:
                        if output[0].startswith("data:"):
                            b64_part = output[0].split(",", 1)[1]
                            return base64.b64decode(b64_part)
                        else:
                            img_resp = client.get(output[0])
                            img_resp.raise_for_status()
                            return img_resp.content
                    raise RuntimeError("FASHN completed but returned no image.")

                if status_data["status"] == "failed":
                    msg = "The try-on generation failed."
                    if status_data.get("error"):
                        msg = status_data["error"].get("message", msg)
                    raise RuntimeError(msg)

            raise RuntimeError("FASHN try-on timed out.")
