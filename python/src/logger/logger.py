import abc


class Logger(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def log(self):
        pass
