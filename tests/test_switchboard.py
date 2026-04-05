import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_local_to_local_call_is_not_cross_border() -> None:
    switchboard = Switchboard()
    active_call = switchboard.register_call(
        "10,Alice,+79001112233,11,Bob,+79004445566"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert switchboard.get_cross_border_calls_count() == 0


def test_foreign_to_foreign_call_is_not_cross_border() -> None:
    switchboard = Switchboard()
    active_call = switchboard.register_call(
        "50,User1,+49123,51,User2,+33987"
    )

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert switchboard.get_cross_border_calls_count() == 0


def test_foreign_to_local_call_is_cross_border() -> None:
    switchboard = Switchboard()
    active_call = switchboard.register_call(
        "20,John,+15550001111,21,Olga,+79998887766"
    )

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert active_call.is_cross_border is True
    assert switchboard.get_cross_border_calls_count() == 1


def test_user_data_integrity() -> None:
    switchboard = Switchboard()
    raw = "999,Test User,+71234567890,888,Receiver Name,+33987654321"
    active_call = switchboard.register_call(raw)

    assert active_call.caller.id == 999
    assert active_call.caller.fullname == "Test User"
    assert active_call.caller.phone == "+71234567890"

    assert active_call.receiver.id == 888
    assert active_call.receiver.fullname == "Receiver Name"
    assert active_call.receiver.phone == "+33987654321"


def test_id_conversion_to_int() -> None:
    switchboard = Switchboard()
    active_call = switchboard.register_call(
        "123,Name,+7111,456,Name2,+7222"
    )

    assert isinstance(active_call.caller.id, int)
    assert isinstance(active_call.receiver.id, int)
    assert active_call.caller.id == 123
    assert active_call.receiver.id == 456


def test_switchboard_state_isolation() -> None:
    sb1 = Switchboard()
    sb1.register_call("1,A,+71,2,B,+72")
    sb1.register_call("3,C,+73,4,D,+14")

    sb2 = Switchboard()
    assert sb2.get_active_calls_count() == 0
    assert sb2.get_cross_border_calls_count() == 0

    assert sb1.get_active_calls_count() == 2
    assert sb1.get_cross_border_calls_count() == 1


def test_register_call_raises_error_on_too_few_fields() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan,+79990000000,2,Petr"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_too_many_fields() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan,+79990000000,2,Petr,+78880000000,extra_field"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_non_digit_caller_id() -> None:
    switchboard = Switchboard()
    invalid_call = "abc,Ivan,+79990000000,2,Petr,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_non_digit_receiver_id() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan,+79990000000,xyz,Petr,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_caller_phone_without_plus() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan,79990000000,2,Petr,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_receiver_phone_without_plus() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan,+79990000000,2,Petr,78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_preserves_state_after_error() -> None:
    switchboard = Switchboard()

    switchboard.register_call("1,Ivan,+79990000000,2,Petr,+78880000000")
    assert switchboard.get_active_calls_count() == 1

    with pytest.raises(ValueError):
        switchboard.register_call("invalid_call")

    assert switchboard.get_active_calls_count() == 1


def test_register_call_raises_error_on_lowercase_caller_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,ivan ivanov,+79990000000,2,Petr Petrov,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_lowercase_receiver_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan Ivanov,+79990000000,2,petr petrov,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_uppercase_caller_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,IVAN IVANOV,+79990000000,2,Petr Petrov,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_uppercase_receiver_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan Ivanov,+79990000000,2,PETR PETROV,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_mixed_case_caller_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,iVan IvAnOv,+79990000000,2,Petr Petrov,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_empty_caller_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,,+79990000000,2,Petr Petrov,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)


def test_register_call_raises_error_on_empty_receiver_name() -> None:
    switchboard = Switchboard()
    invalid_call = "1,Ivan Ivanov,+79990000000,2,,+78880000000"

    with pytest.raises(ValueError):
        switchboard.register_call(invalid_call)
