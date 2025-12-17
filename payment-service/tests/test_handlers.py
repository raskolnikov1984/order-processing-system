import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.payment_service.events.handlers import handle_inventory_reserved
from src.payment_service.models.events import (
    PaymentFailedEvent, PaymentProcessedEvent)


@pytest.mark.anyio
@patch("src.payment_service.events.handlers.publish_payment_failed")
@patch("src.payment_service.events.handlers.publish_payment_processed")
@patch("src.payment_service.events.handlers.payment_processor")
async def test_handle_inventory_reserved_payment_success(
    mock_payment_processor,
    mock_publish_processed,
    mock_publish_failed,
    inventory_reserved_event
):
    """
    Test pago exitoso en primer intento
    """

    mock_payment_processor.process = AsyncMock(
        return_value=(True, "pay_123", None)
    )

    mock_publish_processed.return_value = None
    mock_publish_failed.return_value = None

    await handle_inventory_reserved(inventory_reserved_event)
    await asyncio.sleep(0.3)

    mock_payment_processor.process.assert_called_once_with(
        order_id="test-123",
        amount=99.99,
        retry_count=0
    )

    mock_publish_processed.assert_called_once()
    mock_publish_failed.assert_not_called()

    event_arg = mock_publish_processed.call_args[0][0]
    assert isinstance(event_arg, PaymentProcessedEvent)
    assert event_arg.order_id == "test-123"
    assert event_arg.amount == 99.99


@pytest.mark.anyio
@patch("src.payment_service.events.handlers.publish_payment_failed")
@patch("src.payment_service.events.handlers.publish_payment_processed")
@patch("src.payment_service.events.handlers.payment_processor")
async def test_handle_inventory_reserved_payment_failure_with_retries(
    mock_payment_processor,
    mock_publish_processed,
    mock_publish_failed,
    inventory_reserved_event
):
    """
    ✅ Test pago fallido después de 3 retries
    """
    mock_payment_processor.process = AsyncMock(
        side_effect=[
            (False, None, "Gateway timeout"),
            (False, None, "Insufficient funds"),
            (False, None, "Card declined"),
            (False, None, "Max retries reached")
        ]
    )

    mock_publish_processed.return_value = None
    mock_publish_failed.return_value = None

    await handle_inventory_reserved(inventory_reserved_event)
    await asyncio.sleep(4)

    assert mock_payment_processor.process.call_count == 4
    mock_publish_processed.assert_not_called()
    mock_publish_failed.assert_called_once()

    event_arg = mock_publish_failed.call_args[0][0]
    assert isinstance(event_arg, PaymentFailedEvent)
    assert event_arg.retry_count == 4
    assert "Max retries reached" in event_arg.reason


@pytest.mark.anyio
@patch("src.payment_service.events.handlers.publish_payment_failed")
@patch("src.payment_service.events.handlers.payment_processor")
async def test_handle_inventory_reserved_critical_error(
    mock_payment_processor,
    mock_publish_failed,
    inventory_reserved_event
):
    """
    Test manejo de excepción inesperada
    """

    mock_payment_processor.process = AsyncMock(
        side_effect=Exception("Unexpected gateway error")
    )
    mock_publish_failed.return_value = None

    await handle_inventory_reserved(
        inventory_reserved_event)
    await asyncio.sleep(0.3)

    mock_publish_failed.assert_called_once()

    event_arg = mock_publish_failed.call_args[0][0]
    assert isinstance(event_arg, PaymentFailedEvent)
    assert "Critical error" in event_arg.reason
    assert "Unexpected gateway error" in event_arg.reason
