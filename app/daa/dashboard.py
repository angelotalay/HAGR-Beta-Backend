from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
	"""
	Custom index dashboard for daa.
	"""
	def init_with_context(self, context):
		site_name = get_admin_site_name(context)
		# append a link list module for "quick links"
		self.children.append(modules.LinkList(
			_('Quick links'),
			layout='inline',
			draggable=False,
			deletable=False,
			collapsible=False,
			children=[
				[_('Return to site'), '/'],
				[_('Change password'),
				 reverse('%s:password_change' % site_name)],
				[_('Log out'), reverse('%s:logout' % site_name)],
			]
		))

		self.children.append(modules.Group(
			title='Curation',
			deletable = False,
			draggable=False,
			display = 'tabs',
			children = [
				modules.Group(
					title = 'The Digital Ageing Atlas',
					display = 'stacked',
					children = [ 
						modules.ModelList(
							title='Database',
							models=('daa.atlas.models.Change', 'daa.atlas.models.Relationship', 'daa.atlas.models.Gene', 'daa.atlas.models.Tissue'),
						),
						modules.LinkList(
							title = 'Actions',
							children = (
								[u'\u2611 Check changes for issues', 'atlas/change/check'],
								[u'\u2611 Check changes for referencing issues', 'atlas/change/check_references'],
								[u'\u2611 Check and indicate genes in both GenAge and the DAA', 'atlas/gene/genage'],
								[u'\u21F2 Import changes from CSV', reverse('admin:atlas_import_changes')],
							)
						)
					]
				),
				modules.Group(
					title = 'GenAge',
					display = 'stacked',
					children = [
						modules.ModelList(
							title='Database',
							models=('daa.genage_human.models.Name', 'daa.genage_model.models.Model'),
						),
						modules.LinkList(
							title = 'Actions',
							children = (
								[u'\u2611 Check model organisms for issues', reverse('admin:genage_model_checks')],
								[u'\u21f2 Import Model Organisms', reverse('admin:genage_csvimport')],
								[u'\u21f2 Update longevity entries', reverse('admin:genage_csvupdate')],
								[u'\u21f1 Export GenAge Human entries', reverse('admin:genage_human_export')],
								[u'\u21f1 Export GenAge Model entries', reverse('admin:genage_models_export')],
							)
						)
					]
				),
				modules.Group(
					title = 'AnAge',
					display = 'stacked',
					children = [
						modules.ModelList(
							title='Database',
							models=('daa.anage.models.AnageName', 'daa.anage.models.AnageBiblio',),
						),
						modules.LinkList(
							title = 'Actions',
							children = (
								['No Actions', '#'],
							)
						)
					]
				),
				modules.Group(
					title = 'GenDR',
					display = 'stacked',
					children = [
						modules.ModelList(
							title='Database',
							models=('daa.gendr.models.Gene', 'daa.gendr.models.Expression',),
						),
						modules.LinkList(
							title = 'Actions',
							children = (
								[u'\u2611 Check gene manipulation for issues', reverse('admin:gene_manip_check')],
								[u'\u21f1 Export GenDR manipulations entries', reverse('admin:gendr_manip_export')],
								[u'\u21f1 Export GenDR expression entries', reverse('admin:gendr_exp_export')],
							)
						)
					]
				),
				modules.Group(
					title = 'LongevityMap',
					display = 'stacked',
					children = [
						modules.ModelList(
							title='Database',
							models=('daa.longevity.models.Variant', 'daa.longevity.models.VariantGroup', 'daa.longevity.models.Gene', 'daa.longevity.models.Population',), 
						),
                                                modules.LinkList(
                                                        title = 'Actions',
                                                        children = (
                                                                [u'\u21f2 Import Longevity entries', reverse('admin:longevity_csvimport')],
                                                                [u'\u21f2 Export Longevity entries', reverse('admin:longevity_csvexport')],
                                                        )
                                                )
					]
				),
				modules.Group(
					title = 'LibAge',
					display = 'stacked',
					children = [
						modules.ModelList(
							title='Database',
							models=('daa.django_libage.models.BibliographicEntry', 'daa.django_libage.models.Citation', 'daa.django_libage.models.Source',),
						),
						modules.LinkList(
							title = 'Actions',
						)
					]
				),
                                modules.Group(
                                        title = 'DrugAge',
                                        display = 'stacked',
                                        children = [
                                                modules.ModelList(
                                                        title='Database',
                                                        models=('daa.drugage.models.DrugAgeResults', 'daa.drugage.models.DrugAgeBiblio','daa.drugage.models.DrugAgeCompounds','daa.drugage.models.DrugAgeCompoundSynonyms', 'daa.drugage.models.AverageLifespan', 'daa.drugage.models.MaxLifespan')
                                                ),
                                                modules.LinkList(
                                                        title = 'Actions',
                                                        children = (
                                                                [u'\u21f2 Import DrugAge', reverse('admin:drugage_csvimport')],
                                                                [u'\u21f1 Export DrugAge', reverse('admin:drugage_csvexport')],
                                                        )
                                                )
                                        ]
                                ),
                                modules.Group(
                                        title = 'CellAge',
                                        display = 'stacked',
                                        children = [
                                                modules.ModelList(
                                                        title='Database',
                                                        models=('daa.cellage.models.CellAgeGene','daa.cellage.models.CellAgeMethod','daa.cellage.models.CellAgeSenescence','daa.cellage.models.CellAgeCell','daa.cellage.models.CellAgeCellLine','daa.cellage.models.CellAgeBiblio','daa.cellage.models.CellAgeGeneInterventions'),
                                                ),
                                                modules.LinkList(
                                                        title = 'Actions',
                                                        children = (
                                                                [u'\u21f2 Import Interventions', reverse('admin:cellage_csvimport')],
                                                                [u'\u21f1 Export Interventions', reverse('admin:cellage_csvexport')],
                                                        )
                                                )
                                        ]
                                ),
				modules.AppList(
					_('Administration'),
					deletable=False,
					models=('django.contrib.*',),
				),
			]
		))

		# append a recent actions module
		self.children.append(modules.RecentActions(_('Recent Actions'), 5, deletable=False, draggable=False,))


class CustomAppIndexDashboard(AppIndexDashboard):
	"""
	Custom app index dashboard for daa.
	"""

	# we disable title because its redundant with the model list module
	title = ''

	def __init__(self, *args, **kwargs):
		AppIndexDashboard.__init__(self, *args, **kwargs)

		if self.app_title == 'Atlas':
			apptitle = 'Digital Ageing Atlas'
			models = ('daa.atlas.models.Change', 'daa.atlas.models.Gene', 'daa.atlas.models.Tissue', 'daa.atlas.models.Relationship')
		else:
			apptitle = self.app_title 
			models = self.models

		# append a model list module and a recent actions module
		self.children += [
			modules.ModelList(apptitle, models, deletable=False),
			modules.RecentActions(
				_('Recent Actions'),
				include_list=self.get_app_content_types(),
				limit=5,
				deletable = False
			)
		]

	def init_with_context(self, context):
		"""
		Use this method if you need to access the request context.
		"""
		return super(CustomAppIndexDashboard, self).init_with_context(context)
