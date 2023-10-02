import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from daa.submissions.models import Submission
from daa.django_libage.models import Source

VALID_STORE_GENERAL = (
    'identifier',
    'pubmed',
    )

VALID_STORE_GENMOD = (
    'organism',
    'lifespan_effect',
    'phenotype_description',
    'longevity_influence',
    'max_lifespan_change',
    'avg_lifespan_change',
    'max_lifespan_change_desc',
    'avg_lifespan_change_desc',
    'method',
    )

VALID_STORE_GENDR = (
    'organism',
    'description',
    )

VALID_STORE_LONG = (
    'association',
    'population',
    'study_design',
    'conclusions',
    )

VALID_STORE = VALID_STORE_GENERAL + VALID_STORE_GENMOD + VALID_STORE_GENDR + VALID_STORE_LONG

@csrf_exempt
def index(request):
    if request.method == 'POST':
        store = {}
        for k,v in request.POST.iteritems():
            if k in VALID_STORE:
                store[k] = v
        jsonified = json.dumps(store)
        
        sn = request.POST.get('name') if 'name' in request.POST else None
        se = request.POST.get('email') if 'email' in request.POST else None

        db = request.POST.get('database')

        s = Submission(submitter_name=sn, submitter_email=se, database=db, submission=jsonified) 
        s.save()

        return render(request, 'thankyou.html', {'db': Source.objects.get(short_name=db)})
    return HttpResponse(status=405) 
