import os
import django
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daa.settings")
django.setup()

from daa.drugage.models import DrugAgeResults


def clean_pvalue(pvalue):
    if pvalue:
        return pvalue.replace(u'\xa0', '').replace(" ", "").strip().lower()
    return None


def map_pvalue_to_choice(pvalue):
    if not pvalue:
        return None

    if 'ns' in pvalue or 'n.s.' in pvalue or 'non-significant' in pvalue:
        return "NS"


    # Extract numeric part from pvalue
    try:
        numeric_part = float(re.findall(r"[\d.]+(?:e-?\d+)?", pvalue)[0])
    except (IndexError, ValueError):
        return "NS"  # Return NS if there's no numeric part or if it's not a valid float

    # Compare numeric_part to thresholds and return the corresponding string
    if numeric_part <= 0.0001:
        return "p<0.0001"
    elif numeric_part <= 0.001:
        return "p<0.001"
    elif numeric_part <= 0.01:
        return "p<0.01"
    elif numeric_part <= 0.05:
        return "p<0.05"
    else:
        return "NS"

# Fetch all records (consider using .iterator() for very large datasets)
records = DrugAgeResults.objects.all()

# Process records in memory
for record in records:
    cleaned_pvalue = clean_pvalue(record.pvalue)
    mapped_pvalue = map_pvalue_to_choice(cleaned_pvalue)

    # Update fields based on your conditions
    if record.avg_lifespan_p_value is not None or record.max_lifespan_p_value is not None:
        continue
    if record.avg_lifespan_change_percent is not None and record.max_lifespan_change_percent is None:
        record.avg_lifespan_p_value = mapped_pvalue
    elif record.avg_lifespan_change_percent is None and record.max_lifespan_change_percent is not None:
        record.max_lifespan_p_value = mapped_pvalue
    elif record.avg_lifespan_change_percent is not None and record.max_lifespan_change_percent is not None:
        record.avg_lifespan_p_value = mapped_pvalue
    record.save()
