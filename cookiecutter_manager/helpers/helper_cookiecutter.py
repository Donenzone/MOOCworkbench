from cookiecutter.main import cookiecutter


def clone_cookiecutter_template(cookiecutter_template, repo_dir, project_name, author_name, description=''):
    extra_context = {'project_name': project_name}
    extra_context['author_name'] = author_name
    extra_context['description'] = description
    extra_context['repo_name'] = project_name
    cookiecutter(cookiecutter_template.location,
                 no_input=True,
                 extra_context=extra_context,
                 output_dir=repo_dir,
                 overwrite_if_exists=True)
