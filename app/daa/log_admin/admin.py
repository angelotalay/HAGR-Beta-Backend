from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse

class ActionListFilter(admin.SimpleListFilter):
    title = 'action taken'

    parameter_name = 'action_taken'

    # 1 = add
    # 2 = change
    # 3 = delete
    def lookups(self, request, model_admin):
        return (
            (1, 'addition'),
            (2, 'changed'),
            (3, 'deleted'),
        )

    def queryset(self, request, queryset):
        if self.value() in ('1', '2', '3'):
            return queryset.filter(action_flag=self.value())
        else:
            return queryset


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    readonly_fields = LogEntry._meta.get_all_field_names() + ['object_link', 'action_description']

    list_filter = [
        'user',
        'content_type',
        #'action_flag'
        ActionListFilter,
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'action_description',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            try:
                link = u'<a href="{0}">{1}</a>'.format(
                    reverse('admin:{0}_{1}_change'.format(ct.app_label, ct.model), args=[obj.object_id]),
                    escape(obj.object_repr),
                )
            except:
                link = ''
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def action_description(self, obj):
        action_names = {
            ADDITION: 'Addition',
            DELETION: 'Deletion',
            CHANGE: 'Change',
        }
        return action_names[obj.action_flag]
    action_description.short_description = 'Action'

admin.site.register(LogEntry, LogEntryAdmin)
