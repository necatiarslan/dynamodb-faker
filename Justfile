#initial setup
#install brew
#brew install pyenv
#brew install pyenv-virtualenv
set shell := ["zsh", "-cu"]
set positional-arguments

run:
    pyenv activate dynamodb-faker
    ~/.pyenv/versions/3.11.6/envs/dynamodb-faker/bin/python ~/GitHub/dynamodb-faker/tests/test_dynamodbfaker.py

pip-install:
    pipenv lock --dev
    pipenv sync --dev
    pipenv requirements > requirements.txt --dev
    pipenv clean

pip-check:
    pipenv check #pipfile
    pipenv verify #pipfile.lock

pip-clean:
    pipenv clean

pip-graph:
    pipenv graph


#show active version
pyenv-version:
    pyenv version

#list local pythons
pyenv-versions:
    pyenv versions

#list of available python distros
pyenv-install-menu:
    pyenv install --list | grep " 3."

#install new python version
pyenv-install *args='':
    pyenv install -v $@

pyenv-uninstall *args='':
    pyenv uninstall -v $@

#provide python version
pyenv-virtualenv-create:
    pyenv virtualenv 3.13.0 $(basename $(pwd))
    pyenv activate $(basename $(pwd))
    pyenv local $(basename $(pwd))

pyenv-virtualenv-list:
    pyenv virtualenvs

pyenv-virtualenv-activate:
    pyenv activate $(basename $(pwd))

pyenv-virtualenv-deactivate:
    pyenv deactivate $(basename $(pwd))

pyenv-virtualenv-uninstall:
    pyenv virtualenv-delete $(basename $(pwd))

pyenv-current-virtualenv:
    pyenv shell
    pyenv local
    pyenv version

test:
    pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=dynamodbfaker tests
    pipenv run coverage xml -i

build:
    python setup.py sdist bdist_wheel

publish:
	twine upload dist/1.1.0/*
# Set your username to __token__
# Set your password to the token value, including the pypi- prefix

flake8:
	python -m flake8 dynamodbfaker

pip-install-dynamodbfaker:
    pip install ~/GitHub/dynamodb-faker/dist/dynamodbfaker-1.0.1-py3-none-any.whl --force-reinstall

clean-files:
    find tests/exports -type f -name "*.*" -exec rm {} \;

test-cli:
    dynamodbfaker --config ~/GitHub/dynamodb-faker/tests/test_cli.yaml --target ~/GitHub/dynamodb-faker/tests/exports
