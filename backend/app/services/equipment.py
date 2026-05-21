import json
from pathlib import Path

from app.models.schemas import Equipment


class EquipmentService:
    def __init__(self) -> None:
        path = Path(__file__).resolve().parent.parent / "data" / "equipment.json"
        with open(path) as f:
            items = json.load(f)
        self._by_id = {e["id"]: Equipment(**e) for e in items}
        self._by_qr = {e["qr_payload"]: Equipment(**e) for e in items}

    def get(self, equipment_id: str) -> Equipment | None:
        return self._by_id.get(equipment_id)

    def resolve_qr(self, payload: str) -> Equipment | None:
        payload = payload.strip()
        if payload in self._by_qr:
            return self._by_qr[payload]
        # Allow raw asset id in QR
        if payload.startswith("fieldtech://asset/"):
            return self.get(payload.split("/")[-1])
        return self.get(payload)

    def list_all(self) -> list[Equipment]:
        return list(self._by_id.values())


equipment_service = EquipmentService()
