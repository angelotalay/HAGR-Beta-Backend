class GendrRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'gendr':
            return 'gendr'

    def db_for_write(self, model, **hints):
        "Point all operations on gendr models to 'other'"
        if model._meta.app_label == 'gendr':
            return 'gendr'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in gendr is involved"
        if obj1._meta.app_label == 'gendr' or obj2._meta.app_label == 'gendr':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the gendr app only appears on the 'other' db"
        if db == 'gendr':
            return model._meta.app_label == 'gendr'
        elif model._meta.app_label == 'gendr':
            return False
