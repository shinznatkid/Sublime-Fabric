# coding: utf-8
import os
import sys
import subprocess

try:
    from .fabric_wrapper import fabric_wrapper
except ValueError:
    from fabric_wrapper import fabric_wrapper


class ProcessFab(object):
    def __init__(self, path, task, encoding):
        super(ProcessFab, self).__init__()
        self.path = path
        self.task = task

        dir_path = os.path.dirname(os.path.abspath(self.path))
        query = [fabric_wrapper.fab, self.task, '-f', self.path]
        params = dict(bufsize=1, close_fds='posix' in sys.builtin_module_names,
                      stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                      stdout=subprocess.PIPE,
                      cwd=dir_path)

        self.popen = subprocess.Popen(query, **params)

    def read_data(self):
        return self.popen.stdout.read(1)

    def is_alive(self):
        s = self.popen.poll()
        return s is None

    def kill(self):
        self.popen.kill()
        self.popen.terminate()
