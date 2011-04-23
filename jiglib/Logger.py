__all__=['Logger', 'MultiLogger', 'std_logger']
import sys

# {{{ Logger
class Logger(object):
    def __init__(self, stream=sys.__stdout__, detail_lvl=100):
        if isinstance(stream, str):
            stream = open(stream)
        self.stream     = stream
        self.detail_lvl = detail_lvl

        self.mid_msg = False

    def write(self, msg, detail=0):
        if detail>self.detail_lvl: return
        if self.mid_msg: self.stream.write('\n')

        if isinstance(msg, str):
            self.stream.write(msg)
            self.stream.write('\n')
        elif isinstance(msg, list):
            for m in msg:
                self.stream.write(m)
                self.stream.write('\n')
        self.stream.flush()


    def write_begin(self, msg, detail=0):
        if detail>self.detail_lvl: return
        if self.mid_msg: self.stream.write('\n')

        self.stream.write(msg)
        self.stream.flush()
        self.mid_msg=True

    def write_end(self, msg):
        if not self.mid_msg: return
        self.stream.write(msg)
        self.stream.write('\n')
        self.stream.flush()
        self.mid_msg=False

    def close(self):
        self.stream.close()
# }}}

class MultiLogger(object):
    def __init__(self, loggers=[]):
        self.loggers = loggers
    def write(self, msg, detail=0):
        for logger in self.loggers: logger.write(msg, detail)
    def write_begin(self, msg, detail=0):
        for logger in self.loggers: logger.write_begin(msg, detail)
    def write_end(self, msg):
        for logger in self.loggers: logger.write_end(msg)

std_logger = Logger(detail_lvl=1)  # default logger shouldn't be too verbose

