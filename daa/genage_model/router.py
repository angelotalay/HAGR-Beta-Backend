class GenageRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'genage_model':
            return 'genage_model'

    def db_for_write(self, model, **hints):
        "Point all operations on genage_model models to 'other'"
        if model._meta.app_label == 'genage_model':
            return 'genage_model'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in genage_model is involved"
        if obj1._meta.app_label == 'genage_model' or obj2._meta.app_label == 'genage_model':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the genage_model app only appears on the 'other' db"
        if db == 'genage_model':
            return model._meta.app_label == 'genage_model'
        elif model._meta.app_label == 'genage_model':
            return False
