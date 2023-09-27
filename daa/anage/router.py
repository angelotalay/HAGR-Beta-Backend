class AnageRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'anage':
            return 'anage'

    def db_for_write(self, model, **hints):
        "Point all operations on anage models to 'other'"
        if model._meta.app_label == 'anage':
            return 'anage'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in anage is involved"
        if obj1._meta.app_label == 'anage' or obj2._meta.app_label == 'anage':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the anage app only appears on the 'other' db"
        if db == 'anage':
            return model._meta.app_label == 'anage'
        elif model._meta.app_label == 'anage':
            return False