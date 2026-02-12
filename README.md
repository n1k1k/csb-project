README.md contains the essay for project I for the Cyber Security Base course organised by the University of Helsinki


# Discussion Forum App

This project is a simple discussion forum application. In the app, users can make discussion posts and comments. 
The project is implemented using Python & Django.  

Requirements can be installed using the command:

``pip install -r requirements.txt``

Initialise database using the command:

``python manage.py migrate``

Start the app using the command:

``python manage.py runserver``


### FLAW 1: A02:2021 Cryptographic Failures
[LINK 1](https://github.com/n1k1k/csb-project/blob/e0329fdd2bcea8188737bf5f0d13314de8f0bcde/src/forum/forms.py#L6)

[LINK 2](https://github.com/n1k1k/csb-project/blob/e0329fdd2bcea8188737bf5f0d13314de8f0bcde/src/forum/auth_backend.py#L4) 
(Custom Plaintext Authentication)


Passwords are currently stored in the database as plaintext instead of hash values. This is a serious cryptographic failure.  

Steps to reproduce: 

1. Go to the sign-up page localhost:8000/forum/signup/ 

2. Fill in user information and password 

3. Click sign up 

In order to verify that the passwords are stored as plaintext, do the following:

Open Django shell with command ``python manage.py shell`` and execute the following commands:
1. ``from django.contrib.auth.models import User``
2. ``u = User.objects.last()``
3. ``print(u.password)``


#### HOW TO FIX?
[LINK](https://github.com/n1k1k/csb-project/blob/bfda68f36f4adb71fabc4442ea7514e41142fd06/src/forum/forms.py#L26-L45)

In order to fix this flaw, we need to  replace the unsafe ``SignUpForm`` in ``forms.py``  with a version that hashes the password. One option is to use Django's built-in UserCreationForm that hashes the password:  

```
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user

```

In addition, remove the following plaintext authentication tool from ``settings.py``
```
AUTHENTICATION_BACKENDS = [
    "forum.auth_backend.PlainTextAuthBackend",
]
```

The ``auth_backend.py`` file can, in fact, be completely deleted (but this is not mandatory)  


### FLAW 2: A07:2021 Identification and Authentication Failures

[LINK](https://github.com/n1k1k/csb-project/blob/e0329fdd2bcea8188737bf5f0d13314de8f0bcde/src/mysite/settings.py#L93)

The application permits default, weak, or well-known passwords, such as "password" and passwords that closely resemble other attributes of the user. This makes it easy to get into the accounts of the users who haven't set strong passwords unprompted. 

#### Steps to reproduce

1. Go to the signup page localhost:8000/forum/signup/
2. Fill in username and email
3. Set password as "password"
4. Click submit


#### HOW TO FIX??
[LINK](https://github.com/n1k1k/csb-project/blob/bfda68f36f4adb71fabc4442ea7514e41142fd06/src/mysite/settings.py#L99-L106)

The issue can be fixed by adding the following lines to the AUTH_PASSWORD_VALIDATORS list in the settings.py file

```
{
    "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
 },
 {
    "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
 },
```

NOTE! The fix also requires the changes made to `SignUpForm` in the fix for the previous flaw.


### FLAW 3: A01:2021 Broken Access Control

[LINK](https://github.com/n1k1k/csb-project/blob/d28389d0f91f8cc535322e2b7d98ad42ecbc95d0/src/forum/views.py#L81)

Currently, there is a broken access control issue that allows users to act outside of their intended permissions. The profile page that displays the username along with email is intended to be only viewable to the user in question. The usernames are visible to all when making posts, but this flaw specifically exposes email addresses to malicious actors. Now, anyone can view these pages by changing the id in the URL. 
 

#### Steps to reproduce

1. When logged out go to localhost:8000/forum/profile/user_id/ where user_id is the id of any existing user </br>
   OR </br>
   When logged in, go to localhost:8000/forum/profile/user_id/ where user_id is the id of another user than the one currently logged in

#### HOW TO FIX??

[LINK](https://github.com/n1k1k/csb-project/blob/bfda68f36f4adb71fabc4442ea7514e41142fd06/src/forum/views.py#L83-L97)

The issue can be fixed by first checking if the user is logged in and then checking that the id of the currently logged-in user matches the given id: 

```
  if not request.user.is_authenticated:
      login_url = f"{reverse('login')}?{urlencode({'next': request.get_full_path()})}"
      return redirect(
          login_url, error_message="You must be logged in to view profile"
      )

  if request.user.id != user_id:
      from django.core.exceptions import PermissionDenied

      raise PermissionDenied("You cannot view other users' profiles.")

  user = request.user
```

### FLAW4: A09:2021 – Security Logging and Monitoring Failures

The app does not keep track of failed log in attempts (A09:2021). In fact, there is no limit applied to the login route (A07:2021). A user can attempt to log in an infinite number of times. This means that malicious attackers can access accounts (with weak passwords) by using brute force methods. 

#### HOW TO FIX? 

To fix this, I chose to use the django-axes library to track (and limit) login attempts.

[Step 1](https://github.com/n1k1k/csb-project/blob/e68d27d3664c9ddd1c6c471083602b4214245559/src/mysite/settings.py#L43-L47): Add to INSTALLED_APPS in mysite/settings.py 


```
INSTALLED_APPS = [ 
    'axes', 
    # ... other apps 
]
```
  
[Step 2](https://github.com/n1k1k/csb-project/blob/e68d27d3664c9ddd1c6c471083602b4214245559/src/mysite/settings.py#L60-L64): Add middleware in mysite/settings.py 

 
```
MIDDLEWARE = [ 
    # ... other middleware 
    'axes.middleware.AxesMiddleware', 
] 
```

[Step 3](https://github.com/n1k1k/csb-project/blob/e68d27d3664c9ddd1c6c471083602b4214245559/src/mysite/settings.py#L142-L149): Add axes to ``AUTHENTICATION_BACKENDS`` Configure in ``mysite/settings.py``

```
AUTHENTICATION_BACKENDS += [
     "axes.backends.AxesStandaloneBackend",
]

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_DURATION = timedelta(minutes=30)
AXES_LOCKOUT_TEMPLATE = 'security/lockout.html'
```

[STEP 4](https://github.com/n1k1k/csb-project/blob/e68d27d3664c9ddd1c6c471083602b4214245559/src/mysite/settings.py#L151-L189): Implement logging for failed login attempts. This will write failed attempts into a file called ``security.log``

```
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "security": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "security_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "security.log"),
            "formatter": "security",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "security",
        },
    },
    "loggers": {
        "axes": {
            "handlers": ["security_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "axes.watch_login": {
            "handlers": ["security_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "axes.watch_logins": {
            "handlers": ["security_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```


STEP 5: Run migrations  

``python manage.py migrate axes``

This creates database tables that django-axes needs in order to track login activity. 


### FLAW 5: A03:2021 Injection

[LINK](https://github.com/n1k1k/csb-project/blob/e0329fdd2bcea8188737bf5f0d13314de8f0bcde/src/forum/views.py#L28)

There is a SQL injection vulnerability in the "Add a New Post" Form.

#### Steps to reproduce

1. Log in localhost:8000/accounts/login/ and go to localhost:8000/forum/ 
2. Set the title value to ``test', 'x', 1); PRAGMA foreign_keys=OFF; DELETE FROM forum_post;--``
3. Set content to any string
4. Click submit

#### HOW TO FIX?
[LINK](https://github.com/n1k1k/csb-project/blob/bfda68f36f4adb71fabc4442ea7514e41142fd06/src/forum/views.py#L37-L38)

Currently, the posts are added to the database using executescript() and raw SQL:  
```
sql = f"""
  INSERT INTO forum_post (title, content, user_id)
  VALUES ('{title}', '{content}', {request.user.id});
  """

  with connection.cursor() as cursor:
      cursor.executescript(sql)
```

This is very unsafe and needs to be changed.  There are multiple ways to fix this. One option is to replace the above code with the following ORM:  

```
Post.objects.create(title=title, content=content, user=request.user)
```


