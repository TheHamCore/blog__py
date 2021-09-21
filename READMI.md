### Description
#### a "Blog" project written in Django where authorized users can post and discuss / comment with other users.


#### Install the dependencies and start the server.
```
git clone https://github.com/TheHamCore/blog__py.git
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

#### If you want to launch with a local database you will have to write next command
```python manage.py migrate```

#### Run the server
```
python manage.py runserver
```

***Check your 127.0.0.1:8000***