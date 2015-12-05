import time


class LoggerLevel:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class Logger:

    START_TIME = time.time()
    PRINT_LEVEL = LoggerLevel.DEBUG

    @staticmethod
    def log(log_type, log_time, message):
        if log_type < Logger.PRINT_LEVEL:
            return

        log_message = ""
        if   log_type == LoggerLevel.TRACE:
            log_message += "TRACE"
        elif log_type == LoggerLevel.DEBUG:
            log_message += "DEBUG"
        elif log_type == LoggerLevel.INFO:
            log_message += "INFO "
        elif log_type == LoggerLevel.WARNING:
            log_message += "WARN "
        elif log_type == LoggerLevel.ERROR:
            log_message += "ERROR"
        else:
            return

        log_message += "[%s] " % Logger.timestamp(log_time)
        log_message += message

        print log_message

    @staticmethod
    def timestamp(log_time):
        real_time = 1000 * (time.time() - Logger.START_TIME)
        return "t=%6.5fms(%06.1fms)" % (log_time, real_time)

    @staticmethod
    def trace(time, message):
        Logger.log(LoggerLevel.TRACE, time, message)

    @staticmethod
    def debug(time, message):
        Logger.log(LoggerLevel.DEBUG, time, message)

    @staticmethod
    def info(time, message):
        Logger.log(LoggerLevel.INFO, time, message)

    @staticmethod
    def warning(time, message):
        Logger.log(LoggerLevel.WARNING, time, message)

    @staticmethod
    def error(time, message):
        Logger.log(LoggerLevel.ERROR, time, message)
