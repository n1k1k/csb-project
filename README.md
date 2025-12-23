# Discussion Forum App

This is a simple discussion forum application for the University of Helsinki "Cyber Security Base" course. The app is implemented using Python & Django. 

Requirements can be installed using command
``pip install -r requirements.txt``

Initialise database using command
``python manage.py migrate``

Setup superuser using command
``python manage.py createsuperuser``

Start the app using command
``python manage.py runserver``


### FLAW 1: A03:2021 – Injection

SQL injection vulnerability in the "Add a New Post" Form.
Source link: 

#### Steps to reproduce:

1. Log in and to http://127.0.0.1:8000/forum/ 
Open browser and go to http://localhost:8080
2. Set the title value to ``test', 'x', 1); PRAGMA foreign_keys=OFF; DELETE FROM forum_post;--``
3. Set content to any string
4. Click submit

#### Fix:

The code uses executescript() and raw SQL:
sql = f"""
  INSERT INTO forum_post (title, content, user_id)
  VALUES ('{title}', '{content}', {request.user.id});
  """

  with connection.cursor() as cursor:
      cursor.executescript(sql)


 Instead of this it would be better to use ORM
``Post.objects.create(title=title, content=content, user=request.user)``