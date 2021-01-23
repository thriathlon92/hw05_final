import datetime as dt


def year(request):
    yr = dt.date.today().year
    return {
        'year': yr
    }
