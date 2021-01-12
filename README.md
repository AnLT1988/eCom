How to start a new DJANGO project:
1. Create virtual environment:
virtualenv .\venv
2. Setup git
git init
3. activate virtual envionment and install django
activate.bat
pip install django
4. create a new django project
django-admin project-name <directory>
django-admin eCom . # create a project name eCom in the current folder

# New project structure:
|-root/
|--eCom
|--|-asgi.py
|--|-settings.py
|--|-urls.py
|--|-wsgi.py
|--|-\_\_init\_\_.py
|--manage.py

# Run server
manage.py runserver # start the server at default port 8000
