from budget.models import Budget


def budget(request):
    context_data = None

    try:
        context_data = Budget.objects.get(id=1)
    except Budget.DoesNotExist:
        pass

    return {
        'budget': context_data
    }
