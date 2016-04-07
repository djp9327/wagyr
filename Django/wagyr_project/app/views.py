from django.shortcuts import render_to_response, render
from app.forms import searchGamebyTeam
from app.models import Game, Team
from django.shortcuts import get_list_or_404
from django.db.models import Q
from app.services import api_query_sched, get_create_team, check_sched_loaded
import time
from django.http import HttpResponse, JsonResponse
import datetime


def index(request):
    return render_to_response('bootstrap/index.html')


def about(request):
    return render_to_response('bootstrap/about.html')


def services(request):
    return render_to_response('bootstrap/services.html')


def contact(request):
    return render_to_response('bootstrap/contact.html')


def searchByTeam(request):
    form = searchGamebyTeam()
    return render(request, 'bootstrap/team_schedule.html', {'form': form})


def search(request):
    start = time.time()

    search_term = request.GET['team'].title()

    messages = []
    err = 0
    messages.append("Querying internal DB for Games that the " + str(search_term) + " are playing in")

    # TODO (Ryan) If we add one teams whole schedule, this query will return true for a couple games for every team.
    # need a way to validate that the whole schedule is there

    # FIXED Created an instance method to check if the schedule is loaded

    # Check to see if the team you are searching for has any games, preload team objects if it is found
    games = Game.objects.select_related('home_team', 'away_team').filter(Q(away_team__name__contains=search_term) | Q(home_team__name__contains=search_term))

    if not games:
        api_query = api_query_sched(search_term, messages, err)

        if api_query:
            messages.append("Found " + str(api_query) + " results for future games")
            games = Game.objects.filter(Q(away_team__name__contains=search_term) | Q(home_team__name__contains=search_term))
            end = time.time()
            messages.append("Time elapsed = " + str(end - start) + " seconds")
            return render(request, 'bootstrap/results.html', {'games': games, 'debug': messages, 'errors': err})

        else:
            messages.append("Error getting schedule")
            end = time.time()
            messages.append("Time elapsed = " + str(end - start) + " seconds")
            return render(request, 'bootstrap/results.html', {'debug': messages, 'errors': err})
    else:
        check_sched_loaded(games[0].get_search_team(search_term), messages, err)
        messages.append("Found " + str(games.count()) + " in our database")
        end = time.time()
        messages.append("Time elapsed = " + str(end-start) + " seconds")
        return render(request, 'bootstrap/results.html', {'games': games, 'debug': messages, 'errors': err})


