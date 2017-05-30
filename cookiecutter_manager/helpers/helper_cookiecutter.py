"""Helper to clone a cookiecutter template from a CookieCutterTemplate instance"""
import logging

from cookiecutter.main import cookiecutter

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def clone_cookiecutter_template(cookiecutter_template, repo_dir,
                                project_name, author_name, description=''):
    """Clone a cookiecutter template to directory, overwrites dir if it exists
    :param cookiecutter_template: A CookieCutterTemplate model instance
    :param repo_dir: The location where the cookiecutter dir should be cloned
    :param project_name: The name of the project to be cloned
    :param author_name: Name of the author
    :param description: Short project description (at most 2 lines)"""
    extra_context = {'project_name': project_name}
    extra_context['author_name'] = author_name
    extra_context['description'] = description
    extra_context['repo_name'] = project_name
    logger.debug('starting cookiecutter cloning for template %s in repo dir %s with context %s',
                 cookiecutter_template, repo_dir, extra_context)
    cookiecutter(cookiecutter_template.location,
                 no_input=True,
                 extra_context=extra_context,
                 output_dir=repo_dir,
                 overwrite_if_exists=True)


def clone_cookiecutter_template_with_dict(cookiecutter_template, repo_dir, project_vars):
    """Clone a cookiecutter template with variable extra context in the form of a dictionary
    :param cookiecutter_template: A CookieCutterTemplate model instance
    :param repo_dir: The location where the cookiecutter dir should be cloned
    :param project_vars: The dictionary with the extra context,
    e.g. project name, author name, depending upon which vars
    the cookiecutter template requires"""
    logger.debug('starting cookiecutter cloning for template %s in repo dir %s with context %s',
                 cookiecutter_template, repo_dir, project_vars)
    cookiecutter(cookiecutter_template.location,
                 no_input=True,
                 extra_context=project_vars,
                 output_dir=repo_dir,
                 overwrite_if_exists=True)
