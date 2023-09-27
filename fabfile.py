from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
import datetime

env.hosts = ['ageing-map.org']
env.user = 'thomas'

def deploy():
    local('env/bin/python manage.py collectstatic --noinput')
    local('echo "RELEASE_NUMBER = \'{}\'" > daa/version/release_number.py'.format(datetime.datetime.today().isoformat()))
    local("tar zcvf daa.tar.gz daa/")
    put('daa.tar.gz', '~')
    sudo('mv daa.tar.gz /srv/www/beta.ageing-map.org/')
    with cd('/srv/www/beta.ageing-map.org/'):
        sudo('tar zxvf daa.tar.gz')
        sudo('cp settings.py.template daa/settings.py')
        sudo('cp urls.py.template daa/urls.py')
        sudo('service daa_beta restart')

def deploy_live(redeploy=False):
    local('env/bin/python manage.py collectstatic --noinput')
    if not redeploy:
        local("git tag")
        prompt("Enter a release number:", key='release', validate=r'^v\d\.\d(\.\d)?')
        local("git tag "+env.release)
    local('echo "RELEASE_NUMBER = \'{}\'" > daa/version/release_number.py'.format(env.release))
    local("tar zcvf daa.tar.gz daa/")
    put('daa.tar.gz', '~')
    sudo('mv daa.tar.gz /srv/www/ageing-map.org/')
    with cd('/srv/www/ageing-map.org/'):
        sudo('tar zxvf daa.tar.gz')
        sudo('cp urls.py.template daa/urls.py')
        sudo('cp settings.py.template daa/settings.py')
        sudo('service daa restart')
        #sudo('/etc/init.d/memcached restart')

def reload_live_data(withoutBackup=False):
    with cd('/srv/www/beta.ageing-map.org/'):
        sudo('env/bin/python manage.py export_for_live > live.txt') 

    if not withoutBackup:
        with cd('/srv/www/ageing-map.org/deploy_backups/'):
            filename = datetime.date.today().isoformat()+'-autobackup.tar'
            sudo('pg_dump -F t -f /tmp/{} daa'.format(filename), user='postgres')
            sudo('mv /tmp/{} .'.format(filename))

    with cd('/srv/www/ageing-map.org/'):
        sudo('env/bin/python manage.py truncate_tables')
        sudo('env/bin/python manage.py import_for_live /srv/www/beta.ageing-map.org/live.txt')
