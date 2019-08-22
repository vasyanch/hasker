from .base import *

# Добавим это приложение в INSTALLED_APPS
INSTALLED_APPS = INSTALLED_APPS + [
    'django_jenkins',
]

# Укажем нужные нам ранеры
JENKINS_TASKS = (
    # 'django_jenkins.tasks.with_coverage',
    # 'django_jenkins.tasks.django_tests',
    'django_jenkins.tasks.dir_tests',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_pylint',
    # 'django_jenkins.tasks.run_jslint',
    # 'django_jenkins.tasks.run_csslint',
    # 'django_jenkins.tasks.run_sloccount',
    # 'django_jenkins.tasks.lettuce_tests',
)

# И какие приложения нужно тестировать
PROJECT_APPS = (
    'qa',
    'users',
    'api_haser'
)
