import pytest
from unittest.mock import patch, AsyncMock
from src.inventory_service.events.handlers import handle_order_created


@pytest.mark.anyio
@patch(
    "src.inventory_service.events.handlers.publish_inventory_reserved")
@patch(
    "src.inventory_service.events.handlers.publish_inventory_unavailable")
@patch(
    "src.inventory_service.events.handlers.get_inventory_service")
async def test_handle_order_created_success(
    mock_get_service,
    mock_publish_unavailable,
    mock_publish_reserved,
    order_created_event
):
    """
    Test cuando la reserva de inventario tiene ÉXITO
    """

    mock_service = AsyncMock()
    mock_service.reserve_inventory.return_value = (True, None)
    mock_get_service.return_value = mock_service

    await handle_order_created(order_created_event)

    mock_service.reserve_inventory.assert_called_once()
    mock_publish_reserved.assert_called_once()
    mock_publish_unavailable.assert_not_called()

    event_arg = mock_publish_reserved.call_args[0][0]
    assert event_arg.order_id == "test-123"


@pytest.mark.anyio
@patch(
    "src.inventory_service.events.handlers.publish_inventory_reserved")
@patch(
    "src.inventory_service.events.handlers.publish_inventory_unavailable")
@patch(
    "src.inventory_service.events.handlers.get_inventory_service")
async def test_handle_order_created_insufficient_stock(
    mock_get_service,
    mock_publish_unavailable,
    mock_publish_reserved,
    order_created_event
):
    """
    Test cuando NO hay stock suficiente
    """

    mock_service = AsyncMock()
    mock_service.reserve_inventory.return_value = (
        False,
        "Insufficient stock for prod-1"
    )
    mock_get_service.return_value = mock_service

    await handle_order_created(order_created_event)

    mock_service.reserve_inventory.assert_called_once()
    mock_publish_reserved.assert_not_called()
    mock_publish_unavailable.assert_called_once()

    event_arg = mock_publish_unavailable.call_args[0][0]
    assert event_arg.order_id == "test-123"
    assert "Insufficient stock" in event_arg.reason
