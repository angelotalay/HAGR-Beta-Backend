from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    """
    Custom Menu for daa admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Home'), reverse('admin:index')),
            items.AppList(
                _('DAA'),
                models=('daa.atlas.models.Change', 'daa.atlas.models.Relationship', 'daa.atlas.models.Gene', 'daa.atlas.models.Tissue'),
            ),
            items.AppList(
                _('GenAge'),
                models=('daa.genage_human.models.Name', 'daa.genage_model.models.Model', 'daa.genage_model.models.Biblio'),
                children=[
                    items.MenuItem('Actions', children=[
                        items.MenuItem(u'\u2611 Check model organisms for issues', reverse('admin:genage_model_checks')),
                        items.MenuItem(u'\u21f2 Import Model Organisms', reverse('admin:genage_csvimport')),
                    ]),
                ],
            ),
            items.AppList(
                _('AnAge'),
                models=('daa.anage.models.AnageName', 'daa.anage.models.AnageBiblio',),
            ),
            items.AppList(
                _('GenDR'),
                models=('daa.gendr.models.Gene', 'daa.gendr.models.Expression',),
                children=[
                    items.MenuItem('Actions', children=[
                        items.MenuItem(u'\u2611 Check gene manipulations for issues', reverse('admin:gene_manip_check')),
                    ]),
                ],
            ),
            items.AppList(
                _('LongevityMap'),
                models=('daa.longevity.models.Variant', 'daa.longevity.models.VariantGroup', 'daa.longevity.models.Gene', 'daa.longevity.models.Population',),
            ),
            items.AppList(
                _('LibAge'),
                models=('daa.django_libage.models.BibliographicEntry', 'daa.django_libage.models.Citation', 'daa.django_libage.models.Source',), 
            ),
            items.AppList(
                _('DrugAge'),
                models=('daa.drugage.models.DrugAgeResults', 'daa.drugage.models.DrugAgeBiblio', 'daa.drugage.models.DrugAgeCompounds', 'daa.drugage.models.DrugAgeCompoundSynonyms'),
                children=[
                    items.MenuItem('Actions', children=[
                        items.MenuItem(u'\u21f2 Import DrugAge', reverse('admin:drugage_csvimport')),
                    ]),
                ],
            ),
            items.AppList(
                _('CellAge'),
                models=('daa.cellage.models.CellAgeGene','daa.cellage.models.CellAgeMethod','daa.cellage.models.CellAgeSenescence','daa.cellage.models.CellAgeCell','daa.cellage.models.CellAgeCellLine','daa.cellage.models.CellAgeBiblio','daa.cellage.models.CellAgeGeneInterventions'),
                children=[
                    items.MenuItem('Actions', children=[
                        items.MenuItem(u'\u21f2 Import Interventions', reverse('admin:cellage_csvimport')),
                    ]),
                ],
            ),
            items.AppList(
                _('Application (Full List)'),
                exclude=('django.contrib.*',)
            ),
            items.AppList(
                _('Administration'),
                models=('django.contrib.*',)
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomMenu, self).init_with_context(context)
