import os
import autopep8
import jinja2
import os
import re
from jinja2 import Environment
from jinja2 import PackageLoader
from termcolor import colored


def indent_text(nr, text):
    inds = (' ' * nr)
    return inds + ('\n' + inds).join(text.splitlines())



def package_to_path(package_name):
    """
    Convert package name to relative directory name

    :param package_name:
    :return:
    """
    return package_name.replace('.', os.path.sep)


def render_local_template(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


def fill_file(file_path, context, template=None):
    data = render_local_template(template or file_path, context)
    
    with open(file_path, 'w') as f:
        f.write(data)

def generate_file(filename, template_name, context=None):
    """
    Generates a new file using Jinja2 template

    :param dirname:
    :param template_name:
    :param context:
    :return:
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            match = re.match('^\s*#\s*freeze(\s*,\s+generate\s+to\s*:\s*([a-zA-Z0-9\.\-_]+.py))?', f.read(100))
            if match:
                print('NB! Skipping file {} as it contains #freeze marker'.format(filename))
                if match.group(2):
                    print('NB! Generating to {} instead'.format(match.group(2)))
                    filename = os.path.join(os.path.dirname(filename), match.group(2))
                else:
                    return

    context = context or {}

    def field_names(fields, admin=False):
        names = []
        for field in fields:
            if admin and field.admin_list_renderer:
                names.append('get_{}'.format(field.name))
            else:
                names.append(field.name)

        return format_names(names)

    def format_names(names):
        if not names:
            return ''
        return "'{}'".format("', '".join(names))

    def to_name(ref):
        return ' '.join([x.capitalize() for x in ref.split('_')])

    env = Environment(loader=PackageLoader('cratis_generator', 'templates'))
    env.filters['field_names'] = field_names
    env.filters['format_names'] = format_names
    env.filters['to_name'] = to_name
    env.filters['repr'] = repr

    template = env.get_template(template_name)

    with open(filename, 'w+') as f:
        rendered = template.render(**context)
        if filename.endswith('.py'):
            rendered = autopep8.fix_code(rendered)
        f.write(rendered)



def generate_feature(package_name: str, feature_name: str, extra_context=None):
    """
    Generates new feature

    :param package_name:
    :param name:
    :return:
    """
    assert feature_name

    generate_package(package_name)

    filepath = os.path.join(package_to_path(package_name), 'features.py')

    context = {
        'feature_name': feature_name,
        'package_name': package_name,
        'collection_set': None,
    }
    if extra_context:
        context.update(extra_context)

    generate_file(filepath, 'feature.py.tpl', context)


def generate_package(package_name, path=None):
    if not path:
        path = os.getcwd()

    if not isinstance(package_name, list):
        parts = package_name.split('.')
    else:
        parts = package_name

    dirname = os.path.join(path, parts[0])

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    if not os.path.exists(os.path.join(dirname, '__init__.py')):
        with open(os.path.join(dirname, '__init__.py'), 'w+') as f:
            f.write('\n\n')

    if len(parts) > 1:
        generate_package(parts[1:], dirname)


class StopGenerator(Exception):
    pass


def handle_parse_exception(e, parsed_string, subject):
    print(type(e))
    print('Cannot parse {}, error: {}'.format(subject, e))
    print('-' * 100)
    for nr, line in enumerate(parsed_string.splitlines()):
        if (nr + 1) == e.lineno:
            before = line[:e.col - 1]
            char = line[e.col-1]
            after = line[e.col:]
            line = before + colored(char, 'white', 'on_blue') + after

            print(colored('{0:04d}| {1}'.format(nr + 1, line), 'white', 'on_red'))
        else:
            print('{0:04d}| {1}'.format(nr + 1, line))

    print('-' * 100)
    raise StopGenerator()


def gen_args(args):
    return ', '.join(['{}={}'.format(key, repr(val)) for key, val in args.items()])
