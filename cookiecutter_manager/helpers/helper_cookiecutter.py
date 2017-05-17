import logging
from cookiecutter.main import cookiecutter

logger = logging.getLogger(__name__)


def clone_cookiecutter_template(cookiecutter_template, repo_dir, project_name, author_name, description=''):
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
    logger.debug('starting cookiecutter cloning for template %s in repo dir %s with context %s',
                 cookiecutter_template, repo_dir, project_vars)
    cookiecutter(cookiecutter_template.location,
                 no_input=True,
                 extra_context=project_vars,
                 output_dir=repo_dir,
                 overwrite_if_exists=True)
