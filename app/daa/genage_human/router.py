class GenageRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'genage_human':
            return 'genage_human'

    def db_for_write(self, model, **hints):
        "Point all operations on genage_human models to 'other'"
        if model._meta.app_label == 'genage_human':
            return 'genage_human'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in genage_human is involved"
        if obj1._meta.app_label == 'genage_human' or obj2._meta.app_label == 'genage_human':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the genage_human app only appears on the 'other' db"
        if db == 'genage_human':
            return model._meta.app_label == 'genage_human'
        elif model._meta.app_label == 'genage_human':
            return False
