from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import List, Callable, Optional

from returns.result import safe

from .commands import Command, Create, UpdateValue
from .events import Created, Event, app_event
from .entity import EntityID, Entity

Listener = Callable[[Event], None]


class Repository(ABC):
    @abstractmethod
    def get(self, entity_id: EntityID) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def save(self, entity: Entity) -> None:
        raise NotImplementedError


class CommandHandler:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository
        self._listeners: List[Listener] = []
        super().__init__()

    def register(self, listener: Listener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unregister(self, listener: Listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    @safe
    @singledispatchmethod
    def handle(self, command: Command) -> Optional[Event]:
        entity: Entity = self._repository.get(command.entity_id)

        event: Event = app_event(self._handle(command, entity), command)
        for listener in self._listeners:
            listener(event)

        self._repository.save(entity)
        return event

    @safe
    @handle.register(Create)
    def create(self, command: Create) -> Event:
        entity = Entity.create()
        self._repository.save(entity)
        return Created(command.command_id, entity.id)

    @singledispatchmethod
    def _handle(self, c: Command, u: Entity) -> Entity.Event:
        raise NotImplementedError

    @_handle.register(UpdateValue)
    def _(self, command: UpdateValue, entity: Entity) -> Entity.Event:
        return entity.update(command.value)
