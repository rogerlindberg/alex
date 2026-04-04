import os

from docutils import DataError

import alex


def test_scan():
    assert alex.version == get_version_from_toml()


def get_version_from_toml():
    with open(os.path.join('..', 'pyproject.toml')) as fp:
        lines = fp.read().split('\n')
        state = 0
        for line in lines:
            line = line.strip().lower()
            if state == 0:
                if line.strip().startswith('[project]'):
                    state = 1
            elif state == 1:
                if line.startswith('version'):
                    version_nbr = line.split('=')[-1].strip()[1:-1]
                    return version_nbr
                elif line.startswith('['):
                    raise DataError("Version not found in [project] section")
