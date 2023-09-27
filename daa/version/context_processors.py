from release_number import RELEASE_NUMBER

def version(request):
    return {'version': RELEASE_NUMBER}
