import logging

logger = logging.getLogger(__name__)


class DrugAgeRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'drugage':
            return 'drugage'

    def db_for_write(self, model, **hints):
        "Point all operations on drugage models to 'other'"
        if model._meta.app_label == 'drugage':
            return 'drugage'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in drugage is involved"
        if obj1._meta.app_label == 'drugage' or obj2._meta.app_label == 'drugage':
            return True

    def allow_syncdb(self, db, model):
        if model._meta.app_label == 'drugage':
            if db == 'drugage':
                print("Allowing migration for {} on {}".format(model, db))
                return True
            else:
                print("Blocking migration for {} on {}".format(model, db))
                return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'drugage':
            if db == 'drugage':
                print("Allowing migration for {} on {}".format(app_label, db))
                return True
            else:
                print("Blocking migration for {} on {}".format(app_label, db))
                return False
        return None
