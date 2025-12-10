import requests
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import SearchHistory, FavoriteEvent


API_KEY = 'W1ExhjqiXekAWB0w9wJEU6G4YxwuCKXp'
BASE_URL = 'https://app.ticketmaster.com/discovery/v2/events.json'
PAGE_SIZE = 20


def search_events(request):
    category = request.GET.get('category', '').strip()
    city = request.GET.get('city', '').strip()

    events = []
    total_found = 0
    showed = 0
    error_message = ''

    if category and city:
        params = {
            'apikey': API_KEY,
            'classificationName': category,
            'city': city,
            'sort': 'date,asc',
            'size': PAGE_SIZE,
            'page': 0,
        }

        try:
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            raw_events = data.get('_embedded', {}).get('events', [])
            total_found = data.get('page', {}).get('totalElements', len(raw_events))
            showed = len(raw_events)

            for ev in raw_events:
                name = ev.get('name', 'Untitled event')

                images = ev.get('images', [])
                if images:
                    image_url = images[0].get('url', 'https://via.placeholder.com/640x360')
                else:
                    image_url = 'https://via.placeholder.com/640x360'

                dates = ev.get('dates', {}).get('start', {})
                date_iso = dates.get('dateTime')
                local_time = dates.get('localTime', '')

                # Nice date
                if date_iso:
                    try:
                        dt = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
                        nice_date = dt.strftime('%a %b %d %Y')
                    except Exception:
                        nice_date = 'Date TBA'
                else:
                    nice_date = 'Date TBA'

                # Nice time
                nice_time = ''
                if local_time:
                    try:
                        h_str, m_str, *_ = local_time.split(':')
                        h_int = int(h_str)
                        ampm = 'PM' if h_int >= 12 else 'AM'
                        hour12 = ((h_int + 11) % 12) + 1
                        nice_time = f"{hour12}:{m_str} {ampm}"
                    except Exception:
                        nice_time = local_time

                venue = (ev.get('_embedded', {}) or {}).get('venues', [{}])[0]
                venue_name = venue.get('name', 'Venue TBA')
                addr1 = venue.get('address', {}).get('line1', '')
                city_name = venue.get('city', {}).get('name', '')
                state = venue.get('state', {}).get('stateCode', '')
                parts = [addr1, city_name, state]
                full_addr = ", ".join([p for p in parts if p])

                ticket_url = ev.get('url', '#')

                events.append({
                    'name': name,
                    'image_url': image_url,
                    'nice_date': nice_date,
                    'nice_time': nice_time,
                    'venue_name': venue_name,
                    'full_addr': full_addr,
                    'ticket_url': ticket_url,
                })

            SearchHistory.objects.create(
                genre=category,
                city=city,
                total_results=total_found,
            )

        except requests.RequestException:
            error_message = "Request failed. Please check your API key or inputs."

    elif request.GET:
        error_message = "Please enter both a genre and a city."

    context = {
        'category': category,
        'city': city,
        'events': events,
        'total_found': total_found,
        'shown': showed,
        'page_size': PAGE_SIZE,
        'error_message': error_message,
    }
    return render(request, 'tickets/search.html', context)


# ------------------------------------------------------------
# ⭐ STEP 2 – CRUD VIEWS FOR FAVORITES
# ------------------------------------------------------------

def favorites_list(request):
    favorites = FavoriteEvent.objects.all()
    return render(request, 'tickets/favorites_list.html', {'favorites': favorites})


def add_favorite(request):
    if request.method == "POST":
        name = request.POST.get("name")
        venue = request.POST.get("venue")
        date = request.POST.get("date")
        ticket_url = request.POST.get("ticket_url")
        notes = request.POST.get("notes")

        FavoriteEvent.objects.create(
            name=name,
            venue=venue,
            date=date,
            ticket_url=ticket_url,
            notes=notes,
        )
        return redirect('favorites_list')

    return render(request, 'tickets/add_favorite.html')


def update_favorite(request, pk):
    fav = get_object_or_404(FavoriteEvent, pk=pk)

    if request.method == "POST":
        fav.name = request.POST.get("name")
        fav.venue = request.POST.get("venue")
        fav.date = request.POST.get("date")
        fav.ticket_url = request.POST.get("ticket_url")
        fav.notes = request.POST.get("notes")
        fav.save()
        return redirect('favorites_list')

    return render(request, 'tickets/update_favorite.html', {"fav": fav})


def delete_favorite(request, pk):
    fav = get_object_or_404(FavoriteEvent, pk=pk)
    fav.delete()
    return redirect('favorites_list')
