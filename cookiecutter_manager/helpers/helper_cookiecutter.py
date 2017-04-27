from cookiecutter.main import cookiecutter

from ..models import CookieCutterTemplate


def clone_cookiecutter_data_science(repo_dir, project_name, author_name, description=''):
    template_name = 'https://github.com/drivendata/cookiecutter-data-science'
    _clone_cookiecutter_template(template_name, repo_dir, project_name, author_name, description)


def clone_cookiecutter_pip_package(repo_dir, project_name, author_name, description=''):
    template_name = 'https://github.com/wdm0006/cookiecutter-pipproject'
    _clone_cookiecutter_template(template_name, repo_dir, project_name, author_name, description)


def _clone_cookiecutter_template(cookiecutter_template, repo_dir, project_name, author_name, description=''):
    extra_context = {'project_name': project_name}
    extra_context['author_name'] = author_name
    extra_context['description'] = description
    cookiecutter(cookiecutter_template,
                 no_input=True,
                 extra_context=extra_context,
                 output_dir=repo_dir,
                 overwrite_if_exists=True)

if '__main__':
    clone_cookiecutter_data_science('/home/jochem/Development/MOOCworkbench/github_repositories/',
                                'my-first-project', 'jlmdegoede')