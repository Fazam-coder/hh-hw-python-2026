from __future__ import annotations

from dataclasses import dataclass

from app.users import LocalUser, ForeignUser
from app.users import User


LOCAL_PHONE_PREFIX = "+7"


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


def create_user(user_id: int, user_name: str, user_phone: str) -> User:
    if user_phone[:len(LOCAL_PHONE_PREFIX)] == LOCAL_PHONE_PREFIX:
        user = LocalUser(user_id, user_name, user_phone)
    else:
        user = ForeignUser(user_id, user_name, user_phone)
    return user


class Switchboard:
    def __init__(self) -> None:
        self._active_calls: list[ActiveCall] = []
        self._cross_border_calls: list[ActiveCall] = []

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,reciever_id,reciever_name,reciever_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        caller_id, caller_name, caller_phone, receiver_id, receiver_name, receiver_phone = raw_call.split(",")
        caller = create_user(int(caller_id), caller_name, caller_phone)
        receiver = create_user(int(receiver_id), receiver_name, receiver_phone)
        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)
        if active_call.is_cross_border:
            self._cross_border_calls.append(active_call)
        return active_call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return len(self._cross_border_calls)

