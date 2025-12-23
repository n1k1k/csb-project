# Discussion Forum App

This is a simple discussion forum application for the University of Helsinki "Cyber Security Base" course. The app is implemented using Python & Django. 

Requirements can be installed using command
``pip install -r requirements.txt``

Initialise database using command
``python manage.py migrate``

You can set up a superuser using command
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


### FLAW 2: A01:2021 – Broken Access Control

The profile page that displays the username along with email is intended to be only viewable to the user in question. Now anyone can view these pages by changing the id in the url

[LINK](https://github.com/n1k1k/csb-project/blob/d28389d0f91f8cc535322e2b7d98ad42ecbc95d0/src/forum/views.py#L82)

#### Steps to reproduce

1. When logged out go to http://127.0.0.1:8000/forum/profile/user_id/ where user_id is the id of any existing user </br>
   OR </br>
   When logged in go to http://127.0.0.1:8000/forum/profile/user_id/ where user_id is the id of another user than the one currently logged in

#### How to fix?

The issue can be fixed by first checking if the user is logged in:

```
  if not request.user.is_authenticated:
      login_url = f"{reverse('login')}?{urlencode({'next': request.get_full_path()})}"
      return redirect(
          login_url, error_message="You must be logged in to view profile"
      )
```

Next we need to check that the id of the currently logged in user matches the given id:

```
  if request.user.id != user_id:
      from django.core.exceptions import PermissionDenied

      raise PermissionDenied("You cannot view other users' profiles.")

  user = request.user
```
