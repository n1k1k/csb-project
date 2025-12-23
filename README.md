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

There is a SQL injection vulnerability in the "Add a New Post" Form.


[LINK](https://github.com/n1k1k/csb-project/blob/4f3fffea9cd4e9564fd8c92703336c6c26e28a97/src/forum/views.py#L25)

#### Steps to reproduce

1. Log in and go to http://127.0.0.1:8000/forum/ 
2. Set the title value to ``test', 'x', 1); PRAGMA foreign_keys=OFF; DELETE FROM forum_post;--``
3. Set content to any string
4. Click submit

#### How to fix?

The code uses executescript() and raw SQL:

```
sql = f"""
  INSERT INTO forum_post (title, content, user_id)
  VALUES ('{title}', '{content}', {request.user.id});
  """

  with connection.cursor() as cursor:
      cursor.executescript(sql)
```

There are multiple ways to fix this. One option is to replace the above code with the following ORM:

```
Post.objects.create(title=title, content=content, user=request.user)
```
