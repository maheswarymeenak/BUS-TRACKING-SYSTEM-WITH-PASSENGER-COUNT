from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from bdata.models import Route, Bus, BPoint, BusLoc
import requests

# ✅ Home Page View
def home(request):
    context = {
        "routes": Route.objects.all(),
        "buses": Bus.objects.all()
    }
    return render(request, 'bdata/home.html', context=context)

# ✅ Find Bus View
def find(request):
    if request.method == "POST":
        route_id = request.POST.get("route")
        bpoint_selected_id = request.POST.get("bpoint")

        # Fetch the selected route and boarding point
        buses = Bus.objects.filter(route=route_id)
        bpoint_obj = get_object_or_404(BPoint, id=bpoint_selected_id)

        context = {
            "routes": Route.objects.all(),
            "buses": buses,
            "bpoints": BPoint.objects.all(),
            "bpoint_selected": bpoint_obj
        }
        return render(request, 'bdata/search.html', context=context)

    # Initial page load (GET request)
    context = {
        "routes": Route.objects.all(),
        "buses": Bus.objects.all(),
        "bpoints": BPoint.objects.all()
    }
    return render(request, 'bdata/find.html', context=context)

# ✅ Bus Details View (with Location & Distance Calculation)
def bus(request, bus_id, bpoint):
    bus = get_object_or_404(Bus, id=bus_id)
    bpoint_selected = get_object_or_404(BPoint, id=bpoint)

    # Check if the bus has a location
    bus_loc = getattr(bus, 'busloc', None)
    
    if not bus_loc:  # If no bus location, return an error or default values
        context = {
            "response": {"travelDuration": "N/A", "travelDistance": "N/A"},
            "buses": [bus],  # Pass list to avoid errors
            "bpoint": bpoint_selected,
            "error": "Bus location not available."
        }
        return render(request, 'bdata/bus.html', context=context)

    # Extract latitude and longitude
    bus_lat, bus_long = bus_loc.lat, bus_loc.long
    bpoint_lat, bpoint_long = bpoint_selected.lat, bpoint_selected.long

    # 🔹 Bing Maps API Key
    key = "Ajb5cBYG4DdffO9dIl4wRR3RVQSEhOQ4zOXIGWxURNl24Ro6E9qOgcwGBHwsuW6v"

    # 🔹 Fetch distance and duration from Bing Maps API
    dist_mat = requests.get(f"https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix"
                            f"?origins={bus_lat},{bus_long}&destinations={bpoint_lat},{bpoint_long}"
                            f"&travelMode=driving&key={key}")

    response = dist_mat.json()

    # 🔹 Debugging: Print API response
    print("Bing Maps API Response:", response)

    try:
        travelDuration = round(float(response["resourceSets"][0]["resources"][0]["results"][0]["travelDuration"]), 1)
        travelDistance = int(response["resourceSets"][0]["resources"][0]["results"][0]["travelDistance"])
    except (KeyError, IndexError, ValueError):
        travelDuration = "N/A"
        travelDistance = "N/A"

    context = {
        "response": {"travelDuration": travelDuration, "travelDistance": travelDistance},
        "buses": [bus],  # Pass list format to avoid template errors
        "bpoint": bpoint_selected
    }
    return render(request, 'bdata/bus.html', context=context)

# ✅ Location Update View
def loc(request):
    if request.method == "POST":
        bus_lat = request.POST.get("lat")
        bus_long = request.POST.get("long")

    return render(request, 'bdata/loc.html')

# ✅ Our Team Page
def ot(request):
    return render(request, "bdata/ourteam.html")
