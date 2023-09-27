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
        "Make sure the drugage app only appears on the 'other' db"
        if db == 'drugage':
            return model._meta.app_label == 'drugage'
        elif model._meta.app_label == 'drugage':
            return False
