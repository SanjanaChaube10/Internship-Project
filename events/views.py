from django.shortcuts import render
from .models import Event

# Fallback sample data (25+ Mumbai events) — shown ONLY if DB has no Event rows.
from datetime import datetime
from django.shortcuts import render

SAMPLE_EVENTS = [
        {
            "title": "Fiesta 2026",
            "college_name": "Thakur Polytechnic",
            "date_time": datetime(2026, 1, 24, 10, 0),
            "location": "Kandivali (E)",
            "tag": "Cultural",
            "description": "A vibrant cultural festival celebrating art, music and creativity across two days.",
            "image_url": "https://images.unsplash.com/photo-1511578314322-379afb476865?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "BizCraft Workshop",
            "college_name": "NMIMS",
            "date_time": datetime(2026, 2, 2, 14, 0),
            "location": "Vile Parle",
            "tag": "Workshop",
            "description": "Hands-on business case cracking, presentations, and networking with mentors.",
            "image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Malhar 2026",
            "college_name": "St. Xavier’s College",
            "date_time": datetime(2026, 8, 24, 9, 30),
            "location": "Fort",
            "tag": "Cultural",
            "description": "Mumbai’s legendary intercollegiate festival featuring music, dance, theatre and literary arts.",
            "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "TechNova Hackathon",
            "college_name": "VJTI",
            "date_time": datetime(2026, 3, 14, 9, 0),
            "location": "Matunga",
            "tag": "Tech",
            "description": "24-hour hackathon focused on applied AI, embedded systems and sustainable tech.",
            "image_url": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?q=80&w=1600&auto=format&fit=crop"
        },
        {
        "title": "Agora Cultural Night",
        "college_name": "St. Xavier’s College",
        "date_time":datetime(2026, 3, 14, 9, 0),
        "location": "Fort, Mumbai",
        "tag": "Cultural",
        "description": "Music, theatre, and dance performances by student collectives.",
        "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Pulse Sports Meet",
            "college_name": "Mithibai College",
            "date_time": datetime(2026, 1, 30, 8, 0),
            "location": "Vile Parle (W)",
            "tag": "Sports",
            "description": "Track & field, futsal, basketball and e-sports in a thrilling multi-sport meet.",
            "image_url": "https://images.unsplash.com/photo-1502877338535-766e1452684a?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Symphony Night",
            "college_name": "Jai Hind College",
            "date_time": datetime(2026, 2, 18, 18, 30),
            "location": "Churchgate",
            "tag": "Music",
            "description": "Live bands, indie artists and a capella groups performing under the stars.",
            "image_url": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "DataViz Design Jam",
            "college_name": "K. J. Somaiya College of Engineering",
            "date_time": datetime(2026, 3, 2, 11, 0),
            "location": "Vidyavihar",
            "tag": "Tech",
            "description": "A hands-on dataviz sprint: turn raw datasets into compelling visual stories.",
            "image_url": "https://images.unsplash.com/photo-1517433456452-f9633a875f6f?q=80&w=1600&auto=format&fit=crop"
        },
        {
        "title": "Thakur Aventura",
        "college_name": "Thakur Polytechnic",
        "date_time": datetime(2026, 3, 2, 11, 0),
        "location": "Kandivali (E)",
        "tag": "Sports",
        "description": "Multi-sport event with esports add-on bracket.",
        "image_url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Wilson LitFest",
            "college_name": "Wilson College",
            "date_time": datetime(2026, 2, 9, 10, 0),
            "location": "Charni Road",
            "tag": "Literary",
            "description": "Slams, storytelling, book swaps, and panel discussions with published authors.",
            "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Green Campus Summit",
            "college_name": "Lokmanya Tilak College of Engineering",
            "date_time": datetime(2026, 4, 5, 9, 30),
            "location": "Koparkhairane",
            "tag": "Seminar",
            "description": "Talks & workshops on clean energy, water management and low-carbon campuses.",
            "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1600&auto=format&fit=crop"
        },
        {
        "title": "Sophia Design Jam",
        "college_name": "Sophia College (Autonomous)",
        "date_time": datetime(2026, 4, 5, 9, 30),
        "location": "Breach Candy",
        "tag": "Design",
        "description": "UI/UX rapid prototyping day with mentors.",
        "image_url": "https://images.unsplash.com/photo-1526498460520-4c246339dccb?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "C++ from Zero",
            "college_name": "Vartak Polytechnic",
            "date_time": datetime(2026, 2, 20, 10, 0),
            "location": "Vasai Road",
            "tag": "Workshop",
            "description": "A beginner-friendly day learning modern C++ with hands-on labs.",
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "DroidCraft",
            "college_name": "MIT-WPU",
            "date_time": datetime(2026, 2, 27, 11, 0),
            "location": "Pune",
            "tag": "Tech",
            "description": "Build Android prototypes in teams and present to industry mentors.",
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Brand You",
            "college_name": "HR College of Commerce & Economics",
            "date_time": datetime(2026, 2, 6, 15, 0),
            "location": "Churchgate",
            "tag": "Seminar",
            "description": "Personal branding & LinkedIn strategy workshop for student professionals.",
            "image_url": "https://images.unsplash.com/photo-1492724441997-5dc865305da7?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "SheLeads Tech",
            "college_name": "St. Andrew’s College",
            "date_time": datetime(2026, 3, 8, 10, 0),
            "location": "Bandra (W)",
            "tag": "Seminar",
            "description": "Panel and mentoring sessions with women leaders in technology & product.",
            "image_url": "https://images.unsplash.com/photo-1551836022-4c4c79ecde51?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Stock Strat 101",
            "college_name": "St. Xavier’s College",
            "date_time": datetime(2026, 2, 16, 10, 30),
            "location": "Fort",
            "tag": "Finance Workshop",
            "description": "Risk, reward, and building a mock portfolio—learn equity basics hands-on.",
            "image_url": "https://images.unsplash.com/photo-1559526324-593bc073d938?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "CineMUN",
            "college_name": "Jai Hind College",
            "date_time": datetime(2026, 2, 22, 9, 0),
            "location": "Churchgate",
            "tag": "MUN",
            "description": "A Model UN with a cinematic twist—committees themed around global media.",
            "image_url": "https://images.unsplash.com/photo-1497015289639-54688650d173?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "WebDev Sprint",
            "college_name": "K. J. Somaiya College of Engineering",
            "date_time": datetime(2026, 3, 16, 9, 30),
            "location": "Vidyavihar",
            "tag": "Workshop",
            "description": "React, Tailwind and APIs—build and deploy a working site in one day.",
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "E-Summit Mumbai",
            "college_name": "NMIMS",
            "date_time": datetime(2026, 3, 22, 10, 0),
            "location": "Vile Parle",
            "tag": "Summit",
            "description": "Founders, VCs and workshops—everything entrepreneurship under one roof.",
            "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "EcoTech Expo",
            "college_name": "VJTI",
            "date_time": datetime(2026, 4, 10, 9, 0),
            "location": "Matunga",
            "tag": "Tech Expo",
            "description": "Showcase of green robotics, energy-efficient IoT and sustainable design.",
            "image_url": "https://images.unsplash.com/photo-1509395176047-4a66953fd231?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "SpeakUp Finals",
            "college_name": "Wilson College",
            "date_time": datetime(2026, 2, 28, 13, 0),
            "location": "Charni Road",
            "tag": "Debate",
            "description": "City-wide debate finals—WUDC style with top adjudicators.",
            "image_url": "https://images.unsplash.com/photo-1551836022-37f8b3d16ef2?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Canvas & Coffee",
            "college_name": "Mithibai College",
            "date_time": datetime(2026, 3, 5, 11, 0),
            "location": "Vile Parle (W)",
            "tag": "Arts",
            "description": "Guided acrylic painting session with live music and refreshments.",
            "image_url": "https://images.unsplash.com/photo-1526318472351-c75fcf070305?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Campus Chef",
            "college_name": "Thakur Polytechnic",
            "date_time": datetime(2026, 2, 25, 10, 0),
            "location": "Kandivali (E)",
            "tag": "Food Fest",
            "description": "Cook-off challenge judged by Mumbai food bloggers and chefs.",
            "image_url": "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Build-a-Bot",
            "college_name": "Lokmanya Tilak College of Engineering",
            "date_time": datetime(2026, 3, 12, 9, 30),
            "location": "Koparkhairane",
            "tag": "Robotics",
            "description": "Line follower & sumo bot competitions with live debugging pits.",
            "image_url": "https://images.unsplash.com/photo-1526657782461-9fe13402a841?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "Campus Carnival",
            "college_name": "St. Andrew’s College",
            "date_time": datetime(2026, 2, 23, 16, 0),
            "location": "Bandra (W)",
            "tag": "Fun Fair",
            "description": "Stalls, games, bands and food trucks—family & alumni welcome!",
            "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "AR/VR PlayLab",
            "college_name": "Vartak Polytechnic",
            "date_time": datetime(2026, 3, 9, 10, 0),
            "location": "Vasai Road",
            "tag": "Tech",
            "description": "Create immersive experiences with Unity & WebXR in a guided lab.",
            "image_url": "https://images.unsplash.com/photo-1535223289827-42f1e9919769?q=80&w=1600&auto=format&fit=crop"
        },
        {
            "title": "AI for Creators",
            "college_name": "MIT-WPU",
            "date_time": datetime(2026, 3, 30, 14, 0),
            "location": "Pune",
            "tag": "Seminar",
            "description": "How artists, writers and designers are using AI in their creative pipelines.",
            "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=1600&auto=format&fit=crop"
        },
    ]


def events_page(request):
    # Pull real events if present; otherwise show 25 curated samples.
    qs = Event.objects.select_related("college").order_by("-date_time", "title")
    if qs.exists():
        # Map queryset to the fields the template expects.
        events = [{
            "title": e.title,
            "college_name": e.college.name if hasattr(e, "college") and e.college else "",
            "date_time": e.date_time,
            "location": e.location,
            "tag": "",                # optional: add a CharField in your model if needed
            "description": e.description,
            "image_url": "",          # optional: add ImageField/URLField in your model if needed
        } for e in qs]
    else:
        events = SAMPLE_EVENTS

    return render(request, "events/events_page.html", {"events": events})


from django.db.models import Sum, Count, Prefetch
from django.shortcuts import render
from .models import Sponsor, EventSponsor

from django.shortcuts import render
from .models import Sponsor

def sponsorship_hub(request):
    sponsors = Sponsor.objects.prefetch_related('event_sponsors_event_college')
    return render(request, 'events/sponsorship_hub.html', {'sponsors': sponsors})