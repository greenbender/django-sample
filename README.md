## Django Sample Project ##

A sample Django project that supports per-instance settings and makes it easy
to deploy the project in Dev, QA or Production environments with a minimal
amount of hassle. This sample can be used as a basic template for any Django
project.


### Project layout ###

This sample project is a basic example of project layout the importants parts
of the layout are:

##### sample/settings.py #####

This `settings.py` file supports the use of *per-instance settings.py files* that
are stored in a per-instance directory in the home directory of the user that
the project runs as.

In your project the `settings.py` file can be changed to match your
requirements, however, if there are settings that per-instance configurable
then you should support per-instance configuration for that setting in your
`settings.py` file and ensure that a default value, suitable for development,
is used when a per-instance setting is not supplied. See the `ALLOWED_HOSTS`
and `DATABASE` settings in `sample/settings.py` for examples of how this can be
done.

It is also important that no *secrets* are stored in the `settings.py` file
since it is committed to the project. You can use the `get_path` and `get_data`
helper functions in `settings.py` to help with access secrets that are
appropriately stored (usually in the user home directory with 0600
permissions). The `sample/settings.py` file already does this for the
`SECRET_KEY` setting and as a *bonus* it will generate a secret key for you if
one doesn't exist.

##### resources/... #####

This is where *production* configuration files and templates should be placed.
This sample project has basic templates for `systemd`, `gunicorn` and `nginx`.
Your project may require more configs or different configs (like SSL support
for nginx). Just remember dont't store *secrets* here as these files are
committed to the project.

##### requirements.txt #####

This is a regular `pip` (setuptools) requirements.txt file. Use it to keep
track of *all* your projects python dependencies. This file will be used during
deployment.

##### dependencies.txt #####

This is a list of all your projects *system* dependencies. It could just be a
list of apt packages, but if your project requires a source package or has
other system level (non-python) dependencies you should document them here.
This list can't be used during deployment because that poses a chicken-and-egg
style problem, but it is still helpful to maintain this list.

The sample `dependencies.txt` file simply contains the minimum required apt
packages to deploy the sample project.

##### README.md  #####

This file. At minimum it should supply basic project and deployment information
or point a source of this information.


### Project deployment ###

These are the basic steps to deploy this sample project (and projects based on
this sample).


#### Setup the system ####

```bash
sudo apt update
sudo apt dist-upgrade
sudo apt-get install virtualenv git vim
sudo update-alternatives --set editor /usr/bin/vim.basic
```

#### Project variables ####

Set The name of your Django project. This is the name you used when you ran
`django-admin startproject`.

```bash
export PROJECT_NAME=sample
```

Set the origin for your project.

```bash
export PROJECT_ORIGIN=https://github.com/greenbender/django-sample.git
```

Pick an instance name for your project. Typically this will be the same name as
the Django project but if you are running multiple instances then choose a
unique name.

```bash
export INSTANCE_NAME=${PROJECT_NAME}
```

Set the user for the instance. For development this can be your regualar
user. For production you should use the instance name.

```bash
export INSTANCE_USER=${INSTANCE_NAME}
```

#### Create the virtual environment ####

```bash
sudo virtualenv /opt/${INSTANCE_NAME}-venv
```

#### (Optional) Create a user ####

If you are setting up a development instance this step is optional (you will
have set `INSTANCE_USER` to your username). For production it is best practice to
create a unique user per instance.

```bash
sudo mkdir /opt/${INSTANCE_NAME}-venv/home
sudo adduser --system --group \
    --home /opt/${INSTANCE_NAME}-venv/home/${INSTANCE_USER} \
    --shell=/bin/bash ${INSTANCE_USER}
sudo su ${INSTANCE_USER}
cp /etc/skel/.bash*  ~/
echo ". /opt/${INSTANCE_NAME}-venv/bin/activate" >> ~/.bashrc
echo "set tabstop=4 shiftwidth=4 expandtab" > ~/.vimrc
exit
```

#### Install the Django project ####

Clone the project into the virtual environment and to basic setup. NOTE: If
your project requires additional system packages you should install them prior
to this step.

```bash
sudo mkdir /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}
sudo chown ${INSTANCE_USER}:${INSTANCE_USER} /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}
sudo -u ${INSTANCE_USER} git clone ${PROJECT_ORIGIN} /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}
source /opt/${INSTANCE_NAME}-venv/bin/activate
pip install -r /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}/requirements.txt
sudo su ${INSTANCE_USER}
source /opt/${INSTANCE_NAME}-venv/bin/activate # Only if not already in the virtual environment
/opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}/manage.py migrate # If DB initialisation required
```

For you are deploying a simple project for Development purposes your project is
ready to use now. Run it with `python manage.py runserver`. For complex
projects there may be additional steps which are left as an exercise for the
developer.


#### (Optional) Production Setup ####

1. Setup per-instance `settings.py`

    ```bash
    sudo su ${INSTANCE_USER}
    vim ~/.${INSTANCE_NAME}/settings.py
    # ...
    exit
    ```

2. Setup `gunicorn`

    ```bash
    sudo mkdir /opt/${INSTANCE_NAME}-venv/etc
    sudo cp \
        /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}/resources/gunicorn/gunicorn.conf.py \
        /opt/${INSTANCE_NAME}-venv/etc/
    ```

    Then edit `/opt/${INSTANCE_NAME}-venv/etc/gunicorn.conf.py` to suit your requirements.

3. Setup `systemd`

    ```bash
    sudo mkdir /opt/${INSTANCE_NAME}-venv/run
    sudo cp /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}/resources/systemd/* \
        /etc/systemd/system/
    sudo systemctl enable gunicorn@${INSTANCE_NAME}.socket
    sudo systemctl enable gunicorn@${INSTANCE_NAME}.service
    sudo systemctl start gunicorn@${INSTANCE_NAME}
    ```

    Check for errors using `journalctl -u gunicorn@${INSTANCE_NAME}`
    
4. Setup `nginx`

    ```bash
    sudo apt install nginx
    sudo rm /etc/nginx/sites-enabled/default*
    sudo rm /etc/nginx/sites-available/default*
    sudo cp \
        /opt/${INSTANCE_NAME}-venv/${PROJECT_NAME}/resources/nginx/* \
        /etc/nginx/sites-available/
    for f in /etc/nginx/sites-available/*; do \
        ln -s ../sites-available/${f##*/} /etc/nginx/sites-enabled/${f##*/}; done
    ```

    Then edit the files you have added to `/etc/nginx/sites-enabled/` to suit your requirements.

    ```bash
    sudo systemctl nginx restart
    ```

    Check for errors using `journalctl -u nginx`
