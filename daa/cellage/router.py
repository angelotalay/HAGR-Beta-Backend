class CellAgeRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'cellage':
            return 'cellage'

    def db_for_write(self, model, **hints):
        "Point all operations on cellage models to 'other'"
        if model._meta.app_label == 'cellage':
            return 'cellage'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in cellage is involved"
        if obj1._meta.app_label == 'cellage' or obj2._meta.app_label == 'cellage':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the cellage app only appears on the 'other' db"
        if db == 'cellage':
            return model._meta.app_label == 'cellage'
        elif model._meta.app_label == 'cellage':
            return False
