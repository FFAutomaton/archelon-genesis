import logging
import os


class LimitedLinesFileHandler(logging.FileHandler):
    MAX_LINES = 1000000
    CHECK_INTERVAL = 20000

    def __init__(self, filename, mode='a', encoding=None, delay=False):
        self.max_lines = self.__class__.MAX_LINES
        self.check_interval = self.__class__.CHECK_INTERVAL
        self.line_count = 0
        # If the file exists, determine how many lines it already has.
        if os.path.exists(filename):
            with open(filename, 'r', encoding=encoding) as f:
                self.line_count = sum(1 for _ in f)
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        try:
            super().emit(record)
        except Exception:
            self.handleError(record)
        self.line_count += 1

        if self.line_count % self.check_interval == 0:
            self._truncate_if_necessary()

    def _truncate_if_necessary(self):
        if self.line_count > self.max_lines:
            with open(self.baseFilename, 'r', encoding=self.encoding) as f:
                lines = f.readlines()
            half = len(lines) // 2
            new_lines = lines[half:]
            with open(self.baseFilename, 'w', encoding=self.encoding) as f:
                f.writelines(new_lines)
            self.line_count = len(new_lines)


def get_logger_(coin):
    logger = logging.getLogger(f'{coin}_logger')
    for handler in logger.handlers:
        if getattr(handler, 'name', None) == f'{coin}_logger':
            return logger

    logger.setLevel(logging.INFO)
    file_handler = LimitedLinesFileHandler(f'./log_files/{coin}_bot.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    file_handler.name = f'{coin}_logger'
    logger.addHandler(file_handler)
    return logger

# Example usage:
# if __name__ == '__main__':
#     coin_logger = get_logger_('bitcoin', max_lines=1000, check_interval=100)
#     for i in range(1100):
#         coin_logger.info(f"Log message {i}")
