import fileinput
import os
from os.path import dirname
import sys
import subprocess
import time

# FIXME: test_project_var4 is tmp name
PROJECT_SETTINGS_ABSPATH = os.path.join(dirname(dirname(dirname(__file__))), "test_project_ver4", "settings.py")


def overwrite_project_language(lang_code):
    with fileinput.input(files=(PROJECT_SETTINGS_ABSPATH,), inplace=True) as f:
        for line in f:
            if line.startswith("LANGUAGE_CODE ="):
                print(f'LANGUAGE_CODE = "{lang_code}"')
            else:
                print(line.strip("\n"))


def runtests():
    """Use generatescaffold to generate a model, then run the test
    suite, before finally cleaning up after generatescaffold. Exits
    with the status code of ./manage.py test."""

    app_abspath = os.path.dirname(os.path.dirname(__file__))
    models_abspath = os.path.join(app_abspath, "models.py")
    models_exists = os.path.isfile(models_abspath)
    urls_abspath = os.path.join(app_abspath, "urls.py")
    urls_exists = os.path.isfile(urls_abspath)
    views_abspath = os.path.join(app_abspath, "views")
    views_exists = os.path.isdir(views_abspath)
    tpls_abspath = os.path.join(app_abspath, "templates")
    tpls_exists = os.path.isdir(tpls_abspath)

    for f in [models_abspath, urls_abspath]:
        if os.path.isfile(f):
            subprocess.call(f"cp {f} {f}.orig", shell=True)

    if views_exists:
        subprocess.call(f"cp -r {views_abspath} {views_abspath}.orig", shell=True)

    if tpls_exists:
        subprocess.call(f"cp -r {tpls_abspath} {tpls_abspath}.orig", shell=True)

    overwrite_project_language("ja")
    subprocess.call("python manage.py generatescaffold test_app I18nModel title:string", shell=True)
    time.sleep(1)
    overwrite_project_language("en-us")
    time.sleep(1)

    subprocess.call(
        "python manage.py generatescaffold test_app GeneratedNoTimestampModel title:string description:text --no-timestamps",  # noqa: E501
        shell=True,
    )
    time.sleep(2)  # Give time for Django's AppCache to clear

    subprocess.call(
        "python manage.py generatescaffold test_app GeneratedModel title:string description:text", shell=True
    )

    test_status = subprocess.call(
        "python manage.py test --with-selenium --with-selenium-fixtures --with-cherrypyliveserver --noinput", shell=True
    )

    if models_exists:
        subprocess.call(f"mv {models_abspath}.orig {models_abspath}", shell=True)
    else:
        subprocess.call(f"rm {models_abspath}", shell=True)

    if urls_exists:
        subprocess.call(f"mv {urls_abspath}.orig {urls_abspath}", shell=True)
    else:
        subprocess.call(f"rm {urls_abspath}", shell=True)

    if views_exists:
        subprocess.call(f"rm -rf {views_abspath}", shell=True)
        subprocess.call(f"mv {views_abspath}.orig {views_abspath}", shell=True)
    else:
        subprocess.call(f"rm -rf {views_abspath}", shell=True)

    if tpls_exists:
        subprocess.call(f"rm -rf {tpls_abspath}", shell=True)
        subprocess.call(f"mv {tpls_abspath}.orig {tpls_abspath}", shell=True)
    else:
        subprocess.call(f"rm -rf {tpls_abspath}", shell=True)

    subprocess.call(f"rm {app_abspath}/*.pyc", shell=True)

    sys.exit(test_status)


if __name__ == "__main__":
    runtests()
