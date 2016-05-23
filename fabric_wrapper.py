# coding: utf-8
import os
import subprocess


class TaskException(Exception):
    """
    Raised when cant get tasks from fabfile.
    """


class FabricWrapper(object):
    """
    Wrapper around some fabric apis.
    """
    def __init__(self):
        self._tasks = {}
        self.folders = []

    def set_folders(self, folders):
        self.folders = folders

    @property
    def fab(self):
        try:
            exefab = next(self._get('fab'))[0]
            return exefab if exefab != '' else 'fab'
        except StopIteration:
            return 'fab'

    @property
    def fabfiles(self):
        fabfiles = []
        for f in self._get('fabfile.py'):
            fabfiles.extend(f)
        return list(filter(None, fabfiles))

    def _get(self, filename):
        """
        Find and return (per folder) `filename` in project folders.
        """
        for folder in self.folders:
            ret = []
            for root, _, files in os.walk(folder):
                if filename in files:
                    ret.append(os.path.join(root, filename))
            if ret:
                yield ret

            # file_path = os.path.join(folder, filename)
            # if os.path.isfile(file_path):
            #     yield [file_path]

            # params = ['find', folder, '-name', filename]
            # stdout = subprocess.Popen(params,
            #                           stdout=subprocess.PIPE).stdout.read()
            # found = stdout.decode().split('\n')
            # if found:
            #     yield found

    def get_tasks(self, fabfile_name):
        """
        Return tasks list from fabfile.
        Use simple cache by fabfile abs path & fabfile mtime.
        """
        if self._tasks.get(fabfile_name):
            time, tasks = self._tasks[fabfile_name]
            if time >= os.stat(fabfile_name).st_mtime:
                return tasks

        result = subprocess.Popen(
            [self.fab, '--shortlist', '-f', fabfile_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stdout, stderr = result.stdout.read(), result.stderr.read()

        if stderr:
            raise TaskException(stderr.decode())

        ft = list(filter(None, stdout.decode().split('\n')))
        ft = [x.strip() for x in ft]
        self._tasks[fabfile_name] = (os.stat(fabfile_name).st_mtime, ft)

        return self._tasks[fabfile_name][1]

fabric_wrapper = FabricWrapper()
