import re
import inspect
from collections import OrderedDict, defaultdict


class Sprout(object):
    def __init__(self, celery_app):
        self._celery_app = celery_app

        if not self._celery_app.configured:
            self._celery_app.loader.import_default_modules()

        self._types_map = {
            'datetime.date': 'date',
            'datetime.datetime': 'datetime'
        }

        self._field_description_pattern = \
            re.compile('^:param (.*):\s?(.*)$', re.I)
        self._field_data_type_pattern = \
            re.compile('^:type (.*):\s?(.*)$', re.I)

        self._signatures = None

    @property
    def signatures(self):
        if not self._signatures:
            self._signatures = self.generate_signatures()

        return self._signatures

    @staticmethod
    def _get_docstring(task):
        doc = inspect.getdoc(task)
        if not doc:
            return []
        lines = doc.expandtabs().splitlines()
        lines = filter(lambda x: x, map(lambda x: x.strip(), lines))

        return lines

    @staticmethod
    def _get_description(lines):
        description_lines = []
        for line in lines:
            if line and re.match('^:.*:.*', line):
                break
            description_lines.append(line)

        return '\n'.join(description_lines)

    def _extract_description(self, line, container):
        match = re.search(self._field_description_pattern, line)
        if match:
            name, description = match.groups()
            field_info = {'name': name, 'description': description}
            if name not in container:
                container[name] = field_info
            else:
                container[name].update(field_info)

    def _extract_data_type(self, line, container):
        match = re.search(self._field_data_type_pattern, line)
        if match:
            name, data_type = match.groups()
            data_type = self._types_map.get(data_type, data_type)
            field_info = {'name': name, 'type': data_type}
            if name not in container:
                container[name] = field_info
            else:
                container[name].update(field_info)

    def _extract_fields(self, arg_specs, lines):
        fields = OrderedDict()

        for field_name in arg_specs.args:
            fields[field_name] = {'name': field_name}

        if arg_specs.varargs:
            fields[arg_specs.varargs] = {'name': arg_specs.varargs,
                                         'type': 'args'}

        if arg_specs.keywords:
            fields[arg_specs.keywords] = {'name': arg_specs.keywords,
                                          'type': 'kwargs'}

        for line in lines:
            self._extract_description(line, fields)
            self._extract_data_type(line, fields)

        if arg_specs.defaults:
            for i, value in enumerate(arg_specs.defaults[::-1]):
                field_name = arg_specs.args[- (i + 1)]
                fields[field_name].update({'default': value})

        return fields.values()

    def generate_signatures(self):
        tasks_signatures = defaultdict(list)

        for full_task_name, task in self._celery_app.tasks.items():
            if full_task_name.startswith('celery'):
                continue

            if not hasattr(task, '__wrapped__'):
                continue

            arg_spec = inspect.getargspec(task.__wrapped__)

            module_name = '.'.join(full_task_name.split('.')[:-1])
            task_name = full_task_name.split('.')[-1]

            lines = self._get_docstring(task)
            description = self._get_description(lines)
            fields = self._extract_fields(arg_spec, lines)

            task_signature = {
                'module_name': module_name,
                'fullname': task_name,
                'description': description,
                'fields': fields
            }

            tasks_signatures[module_name].append(task_signature)

        return tasks_signatures
