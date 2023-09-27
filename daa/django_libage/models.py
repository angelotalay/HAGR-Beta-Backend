import urllib

from django.db import models
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist

from daa.fetchscript.fetch import FetchReference

class Source(models.Model):
    class Meta:
        db_table = 'references_source'
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=40)
    url = models.URLField()
    base_url = models.URLField()
    colour = models.CharField(max_length=6, null=True, blank=True)
    hide = models.BooleanField(default=False)

    def get_entries(self):
        return BibliographicEntry.objects.filter(citations__source__name=self.name).distinct()

    def __unicode__(self):
        return self.name+': ('+self.url+')'

class Citation(models.Model):
    class Meta:
        unique_together = ('identifier', 'source',)
        db_table = 'references_citation'
    identifier = models.CharField(max_length=50)
    title = models.CharField(max_length=1024)
    source = models.ForeignKey(Source)
    hide = models.BooleanField(default=False)

    @property
    def citation_source(self):
        return self.source.base_url.format(self.identifier)

    def __unicode__(self):
        return self.identifier+': '+self.title

class Tag(models.Model):
    class Meta:
        db_table = 'references_tag'
    name = models.CharField(max_length=200, db_index=True)

    def get_entries(self):
        return self.bibliographicentry_set.distinct().filter(citations__source__hide=False)

    def __unicode__(self):
        return self.name

class Author(models.Model):
    class Meta:
        db_table = 'references_author'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    initials = models.CharField(max_length=5, null=True, blank=True)

    full_name = models.CharField(max_length=250, null=True, blank=True)

    def get_full_name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    def get_search_field(self):
        encoded_name = urllib.quote_plus(self.__unicode__().encode('utf8'))
        return u'authors:"{}"'.format(encoded_name)

    def save(self, *args, **kwargs):
        self.full_name = u'{} {}'.format(self.first_name, self.last_name)
        super(Author, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)
        
class BibliographicEntryManager(models.Manager):
    """Return a BibliographicEntry instance, creating an entry if non-existant."""
    def get_or_create_from_pubmed(self, pubmed, database='libage'):
        try:
            entry = self.using(database).get(pubmed=pubmed)
        except ObjectDoesNotExist:
            fr = FetchReference()
            details = fr.fetchPubmed(pubmed, withTerms=True)
            terms = details['terms']
            authors = details['authors']
            for i in ('terms', 'author_initials', 'authors'):
                del details[i]
            entry = BibliographicEntry(**details)
            entry.save(using=database)
            for t in terms:
                tg,c = Tag.objects.using(database).get_or_create(name=t)
                entry.tags.add(tg)
            for a in authors:
                author, c = Author.objects.using(database).get_or_create(**a)
                entry.authors.add(author)
        return entry

class BibliographicEntry(models.Model):
    class Meta:
        db_table = 'references_bibliographicentry'
    pubmed = models.CharField(max_length=20, blank=True, null=True, unique=True, db_index=True)
    title = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    url = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    volume = models.CharField(max_length=40, blank=True, null=True)
    pages = models.CharField(max_length=40, blank=True, null=True)
    year = models.PositiveIntegerField(null=True, blank=True, db_index=True, default=0)
    journal = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    issue = models.CharField(max_length=40, blank=True, null=True)
    editor = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    book_title = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    review = models.NullBooleanField()

    contact_addresses = models.CharField(max_length=200, blank=True, null=True)

    authors = models.ManyToManyField(Author)

    citations = models.ManyToManyField(Citation, blank=True, db_index=True)
    tags = models.ManyToManyField(Tag, blank=True)

    date_added = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    objects = BibliographicEntryManager()

    def get_title(self):
        if self.book_title is not None and self.book_title != u'':
            return self.book_title
        return self.title

    def get_author(self):
        if (self.author == u'' or self.author is None) and (self.editor != u'' and self.editor is not None):
            return self.editor
        return self.author

    def get_short_reference(self):
        return u'{0} ({1})'.format(self.author, self.year)

    def formatted_reference(self):
        if self.author != u'' and self.author is not None:
            persons = self.author
        else:
            persons = u''

        if self.volume is not None and self.volume != u'':
            sep = ''
            if self.issue == u'' or self.issue is None:
                sep = ':'
            volume = u' <b>{vol}</b>{sep}'.format(vol=self.volume, sep=sep)
        else:
            volume = ''

        if self.issue is not None and self.issue != u'':
            issue = u"({0}):".format(self.issue)
        else:
            issue = u""

        if self.pubmed != u'' and self.pubmed is not None:
            link = u' <a class="libage-pubmed" href="http://www.ncbi.nlm.nih.gov/pubmed/{0}">(PubMed)</a>'.format(self.pubmed)
        elif self.url != '' and self.url is not None:
            link = u' (<a href="{0}">{0}</a>)'.format(self.url)
        else:
            link = u''

        if self.title != u'' and self.title is not None:
            title = u'"<b>{}</b>" '.format(self.title)
        else:
            title = u''

        if self.book_title != u'' and self.book_title is not None:
            if self.editor != u'' and self.editor is not None:
                book = u' in {editor} (Ed.) <i>{book}</i>'.format(editor=self.editor, book=self.book_title)
            book = u' in <i>{book}</i>'.format(book=self.book_title)
        else:
            book = u''

        if self.journal != u'' and self.journal is not None:
            journal = u' {}'.format(self.journal)
        else:
            journal = u''

        if self.pages != u'' and self.pages is not None:
            pages = u'{}'.format(self.pages)
        else:
            pages = u''

        if self.year != u'' and self.year is not None:
            year = u'({})'.format(self.year) 
        else:
            year = ''

        ref_format = u'{persons} {year} {title}{book}{journal}{volume}{issue}{pages}{link}'.format(persons=persons, year=year, title=title, journal=journal, volume=volume, issue=issue, pages=pages, book=book, link=link)
            
        return mark_safe(ref_format)    

    def reference(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.author != u'' and self.author is not None:
            persons = u'{}'.format(self.author)
        else:
            persons = u''

        if self.volume is not None and self.volume != u'':
            sep = u''
            if self.issue == u'' or self.issue is None:
                sep = ':'
            volume = u' {vol}{sep}'.format(vol=self.volume, sep=sep)
        else:
            volume = ''

        if self.issue is not None and self.issue != u'':
            issue = u"({0}):".format(self.issue)
        else:
            issue = u""

        if self.pubmed != u'' and self.pubmed is not None:
            link = u' ({0})'.format(self.pubmed)
        elif self.url != '' and self.url is not None:
            link = u' ({0})'.format(self.url)
        else:
            link = u''

        if self.title != u'' and self.title is not None:
            title = u'"{}" '.format(self.title)
        else:
            title = u''

        if self.book_title != u'' and self.book_title is not None:
            if self.editor != u'' and self.editor is not None:
                book = u' in {editor} (Ed.) {book}'.format(editor=self.editor, book=self.book_title)
            book = u' in {book}'.format(book=self.book_title)
        else:
            book = u''

        if self.journal != u'' and self.journal is not None:
            journal = u' {}'.format(self.journal)
        else:
            journal = u''

        if self.pages != u'' and self.pages is not None:
            pages = u'{}'.format(self.pages)
        else:
            pages = u''

        if self.year != u'' and self.year is not None:
            year = u'({})'.format(self.year) 
        else:
            year = ''

        ref_format = u'{id}: {persons} {year} {title}{book}{journal}{volume}{issue}{pages}{link}'.format(id=self.id, persons=persons, year=year, title=title, journal=journal, volume=volume, issue=issue, pages=pages, book=book, link=link)

        return ref_format 
