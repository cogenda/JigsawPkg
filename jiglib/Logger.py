__all__=['Logger', 'MultiLogger', 'std_logger', 'cmd_n_log']
import sys, os, subprocess

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

# {{{ cmd_n_log
def cmd_n_log(cmd, splitline=True, logger=None, input=None, **kwargs):

    def _write_log(msg, detail=0):
        if logger==None: return
        logger.write(msg, detail)

    p = subprocess.Popen(cmd, 
                         stdin =subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, **kwargs)
    _write_log('running %s' % cmd)
    out, err = p.communicate(input)
    _write_log('retcode=%d' % p.returncode, 2)

    _write_log(['------output-----', out], 2)
    if len(err):
        _write_log(['------error------', err], 2)
    _write_log('-----------------', 2)

    if not p.returncode==0:
        raise Exception()

    if splitline:
        return out.split('\n')
    else:
        return out
# }}}

