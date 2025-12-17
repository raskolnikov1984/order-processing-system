import pytest


@pytest.fixture
def inventory_reserved_event():
    return {
        "event_id": "evt_2025-12-17",
        "event_type": "InventoryReserved",
        "timestamp": "datetime.datetime(2025, 12, 17, 6, 11, 31, 327200",
        "order_id": "test-123",
        "total_amount": 99.99,
        "reservation_id": "res-789"
    }
