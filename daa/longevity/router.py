class LongevityRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'longevity':
            return 'longevity'

    def db_for_write(self, model, **hints):
        "Point all operations on longevity models to 'other'"
        if model._meta.app_label == 'longevity':
            return 'longevity'

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in longevity is involved"
        if obj1._meta.app_label == 'longevity' or obj2._meta.app_label == 'longevity':
            return True

    def allow_syncdb(self, db, model):
        "Make sure the longevity app only appears on the 'other' db"
        if model._meta.app_label in ['south']:
            return True
        if db == 'longevity':
            return model._meta.app_label == 'longevity'
        elif model._meta.app_label == 'longevity':
            return False
