from typing import List, Dict, Any

from .observers import Observer


class Subject:
    """
    Subject class for the Observer design pattern.
    """

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.

        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.

        Args:
            observer: Observer to detach
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, data: Dict[str, Any] = None) -> None:
        """
        Notify all observers about an event.

        Args:
            data: Data to pass to observers
        """
        for observer in self._observers:
            observer.update(data)