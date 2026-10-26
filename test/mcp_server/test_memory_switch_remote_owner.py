"""memory_store / memory_forget honor the local memory switch before a remote owner is called."""

from unittest.mock import AsyncMock, patch

import pytest

from cli_agent_orchestrator.mcp_server import server as srv

SWITCH = "cli_agent_orchestrator.services.settings_service.is_memory_enabled"
GATEWAY = "cli_agent_orchestrator.services.memory_gateway"


@pytest.mark.asyncio
async def test_store_switch_off_never_reaches_remote_owner():
    with (
        patch(SWITCH, return_value=False),
        patch(f"{GATEWAY}.remote_memory_url", return_value="http://owner:9889"),
        patch(f"{GATEWAY}.store_memory", new_callable=AsyncMock) as remote,
    ):
        result = await srv.memory_store(content="x", scope="global")

    assert result["success"] is False
    assert result["disabled"] is True
    remote.assert_not_called()


@pytest.mark.asyncio
async def test_forget_switch_off_never_reaches_remote_owner():
    with (
        patch(SWITCH, return_value=False),
        patch(f"{GATEWAY}.remote_memory_url", return_value="http://owner:9889"),
        patch(f"{GATEWAY}.forget_memory", new_callable=AsyncMock) as remote,
    ):
        result = await srv.memory_forget(key="k", scope="global")

    assert result["success"] is False
    assert result["disabled"] is True
    remote.assert_not_called()


@pytest.mark.asyncio
async def test_switch_on_still_delegates_to_remote_owner():
    with (
        patch(SWITCH, return_value=True),
        patch(f"{GATEWAY}.remote_memory_url", return_value="http://owner:9889"),
        patch(f"{GATEWAY}.forget_memory", new_callable=AsyncMock) as remote,
    ):
        result = await srv.memory_forget(key="k", scope="global")

    remote.assert_awaited_once()
    assert result["success"] is True
