class LibageRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'django_libage':
            return 'libage'

    def db_for_write(self, model, **hints):
        "Point all operations on libage models to 'other'"
        if model._meta.app_label == 'django_libage':
            return 'libage'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in libage is involved"
        if obj1._meta.app_label == 'django_libage' or obj2._meta.app_label == 'django_libage':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the libage app only appears on the 'other' db"
        if db == 'libage':
            return model._meta.app_label == 'django_libage'
        elif model._meta.app_label == 'django_libage':
            return False
