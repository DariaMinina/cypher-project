import os
from string import Template


class Provider:

    def __init__(self, file_path: str) -> None:
        self._scripts = {}  # = > _scripts = {'book_by_genre': "select * from book ...

        for file in os.listdir(file_path):
            self._scripts[file] = Template(open(f'{file_path}/{file}', 'r').read())

    def get(self, name, **kwargs):
        return self._scripts[name].substitute(**kwargs)
