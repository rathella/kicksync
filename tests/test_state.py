from app.state import (
    INITIAL_RECONNECT_DELAY,
    MAX_RECONNECT_DELAY,
    ConnectionState,
)


def test_initial_connection_state() -> None:
    state = ConnectionState()

    assert state.connected is False
    assert (
        state.reconnect_delay
        == INITIAL_RECONNECT_DELAY
    )


def test_mark_connected_resets_backoff() -> None:
    state = ConnectionState()

    state.reconnect_delay = 16
    state.next_reconnect_at = 123.0

    state.mark_connected()

    assert state.connected is True
    assert (
        state.reconnect_delay
        == INITIAL_RECONNECT_DELAY
    )
    assert state.next_reconnect_at == 0.0


def test_mark_disconnected_schedules_reconnect() -> None:
    state = ConnectionState()

    state.mark_disconnected()

    assert state.connected is False
    assert state.next_reconnect_at > 0.0


def test_backoff_doubles() -> None:
    state = ConnectionState()

    state.increase_backoff()
    assert state.reconnect_delay == 2

    state.increase_backoff()
    assert state.reconnect_delay == 4

    state.increase_backoff()
    assert state.reconnect_delay == 8


def test_backoff_has_maximum() -> None:
    state = ConnectionState()

    for _ in range(20):
        state.increase_backoff()

    assert (
        state.reconnect_delay
        == MAX_RECONNECT_DELAY
    )


def test_connected_state_cannot_reconnect() -> None:
    state = ConnectionState()

    state.mark_connected()

    assert state.can_reconnect() is False