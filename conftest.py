import sys
from subprocess import Popen

import os
from shutil import rmtree, copy
from venv import EnvBuilder

import pytest

from pytest_forked import forked_run_report

from zmei_generator.generator.collections import generate, generate_common_files
from zmei_generator.parser.parser import parse_string, parse_file
from zmei_generator.parser.populate import populate_collection_set

skeleton_dir = os.path.join(os.path.dirname(__file__), 'skeleton')
samples_dir = os.path.join(os.path.dirname(__file__), 'tests/samples')
work_dir_prefix = os.path.join(os.path.dirname(__file__), 'tests/gen_result')
files_dir = os.path.join(os.path.dirname(__file__), 'tests/files')

base_path = os.path.realpath('.')


def pytest_sessionstart(session):
    if os.path.exists(work_dir_prefix):
        rmtree(work_dir_prefix)
    os.mkdir(work_dir_prefix)


def pytest_addoption(parser):
    parser.addoption("--zmei", action="store_true", help="only run tests that are market with col().")


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "zmei(app_name): test requires generated django application from .col file")


def pytest_runtest_teardown(item):
    os.chdir(base_path)


def pytest_runtest_setup(item):
    import sys
    import os

    before = item.get_marker("zmei_before")
    if before:
        commands_before = before.args
    else:
        commands_before = []

    colmarker = item.get_marker("zmei")
    zmei = item.config.getoption("--zmei")

    if zmei and not colmarker:
        pytest.skip("Running only zmei tests")

    if colmarker:
        # prepare workdir
        work_dir = os.path.join(work_dir_prefix, item.name)
        if os.path.exists(work_dir):
            rmtree(work_dir)
        os.mkdir(work_dir)

        collection_set_name = colmarker.args[0]
        if len(colmarker.args) > 1:
            tree = parse_string(colmarker.args[1])
        else:
            col_file = '{}/{}.col'.format(samples_dir, collection_set_name)
            tree = parse_file(col_file)

        collection_set = populate_collection_set(tree, collection_set_name)

        copy('{}/dev.db'.format(files_dir), '{}/dev.db'.format(work_dir, collection_set_name))

        generate_common_files(work_dir, skeleton_dir, {collection_set_name: collection_set})
        generate(work_dir, collection_set_name, collection_set)

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

        add_to_path(work_dir)

        import django
        django.setup()

        for command in commands_before:
            if command == 'migrate':
                call_django_command('makemigrations {}'.format(collection_set_name), work_dir)

            if command == 'install':
                continue
            else:
                call_django_command(command, work_dir)


def add_to_path(work_dir):
    paths_to_delete = []
    for path in sys.path:
        if path.startswith(work_dir_prefix):
            paths_to_delete.append(path)
    for path in paths_to_delete:
        sys.path.remove(path)
    sys.path.append(work_dir)

    print(sys.path)


def call_django_command(django_command, work_dir):
    import sys
    env = os.environ.copy()

    env.update({
        "PYTHONPATH": ":".join([x for x in sys.path if x != ''] + [work_dir]),
    })
    p1 = Popen([sys.executable, 'manage.py'] + django_command.split(' '), env=env, cwd=work_dir)
    p1.wait()


#


@pytest.mark.tryfirst
def pytest_runtest_protocol(item):
    colmarker = item.get_marker("zmei")

    if colmarker:
        reports = forked_run_report(item)
        for rep in reports:
            item.ihook.pytest_runtest_logreport(report=rep)
        return True

# def pytest_runtest_setup(item):
#     envmarker = item.get_marker("env")
#     if envmarker is not None:
#         envname = envmarker.args[0]
#         if envname != item.config.getoption("-E"):
#             pytest.skip("test requires env %r" % envname)
#
