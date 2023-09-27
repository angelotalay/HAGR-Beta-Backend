class OrthologRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ortholog':
            return 'ortholog'

    def db_for_write(self, model, **hints):
        "Point all operations on ortholog models to 'other'"
        if model._meta.app_label == 'ortholog':
            return 'ortholog'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in ortholog is involved"
        if obj1._meta.app_label == 'ortholog' or obj2._meta.app_label == 'ortholog':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the ortholog app only appears on the 'other' db"
        if db == 'ortholog':
            return model._meta.app_label == 'ortholog'
        elif model._meta.app_label == 'ortholog':
            return False
