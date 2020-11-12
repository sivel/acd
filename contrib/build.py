# Copyright (c) 2020 Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+
#     (see https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import os
import string
import subprocess
from urllib.request import urlopen

from jinja2 import Environment

import yaml

ROOT = os.path.dirname(
    os.path.dirname(__file__)
)
LETTERS = frozenset(string.ascii_letters)


def to_nice_yaml(a, indent=4, *args, **kwargs):
    '''Make verbose, human readable yaml'''
    return yaml.dump(a, indent=indent, allow_unicode=True,
                     default_flow_style=False, **kwargs)


e = Environment()
e.filters['to_nice_yaml'] = to_nice_yaml

with open(os.path.join(ROOT, 'galaxy.yml.j2')) as f:
    template = f.read()


url = (
    'https://api.github.com/repos/ansible-community/ansible-build-data'
    '/contents/2.10/'
)

files = json.load(urlopen(url))

for file in files:
    if os.path.splitext(file['name'])[1] != '.deps':
        continue

    try:
        deps = yaml.safe_load(urlopen(file['download_url']))
        version = deps.pop('_ansible_version')
    except AttributeError:
        continue
    deps.pop('_ansible_base_version', None)
    deps.pop('_ansible_core_version', None)

    t = e.from_string(template)
    with open(os.path.join(ROOT, 'galaxy.yml'), 'w+') as f:
        f.write(t.render(version=version, dependencies=deps))

    subprocess.Popen(
        ['ansible-galaxy', 'collection', 'build'],
        cwd=ROOT,
    ).communicate()
