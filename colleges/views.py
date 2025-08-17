# colleges/views.py
from django.shortcuts import render
from django.templatetags.static import static
from .models import College

# simple normalizer for logo lookup keys
def _k(s: str) -> str:
    return (s or "").lower().replace(".", "").replace("’", "'").strip()

def college_event_portal(request):
    """
    Renders the College Events Portal with colleges from DB.
    Since the College model doesn't store a logo, we map known college
    names -> logo URLs. Unknown names get a neutral fallback.
    """
    colleges = College.objects.all().order_by("name")

    logo_map = {
        _k("Thakur Polytechnic"): "https://www.tpolymumbai.in/img/logo/tpoly_logo.png",
        _k("NMIMS"): "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSeRaIpVn5pjMYHS7El8iF46TDQcXgGvLrrvw&s",
        _k("Vartak Polytechnic"): "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQE_-SkDyknm-PMr7TmRdP4Z-GMv-YGakmu0g&s",
        _k("VJTI College"): "https://pbs.twimg.com/profile_images/1700137678719844352/zh_yXP1V_400x400.jpg",
        _k("DyPatil University"): "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTv3y8o2OkfFn3xnID7wKi91ztK5OJUadNpOg&s",
        _k("A. C. Patil College of Engineering"): "https://media.licdn.com/dms/image/v2/D4D0BAQF4ibEJzgOBPA/company-logo_200_200/company-logo_200_200/0/1696739351080?e=2147483647&v=beta&t=SCPaQ9bTjNi1-68qtO7SErMSQL97FZa596n_GAppuG0",
        _k("Lokmanya Tilak College of Engineering"): "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6e0aNa9xPbWelP4sJRRTLq_bWFuY0jAkyrg&s",
        _k("MIT-WPU"): "https://media.collegedekho.com/media/img/institute/logo/android-chrome-192x192.png",

        # your static pack (match what you used in the template)
        _k("Jai Hind College"): static("image/jaihind.png"),
        _k("St. Xavier’s College"): static("image/xavier.png"),
        _k("K. J. Somaiya College of Engineering"): static("image/Somaiya.png"),
        _k("Wilson College"): static("image/wilson.png"),
        _k("Mithibai College"): static("image/mithibai.png"),
        _k("Sophia College (Autonomous)"): static("image/sophia.png"),
        _k("SIES College of Arts, Science & Commerce"): static("image/sies.png"),
        _k("Ramnarain Ruia Autonomous College"): static("image/ruia.png"),
        _k("H.R. College of Commerce & Economics"): static("image/H.R.png"),
        _k("St. Andrew’s College"): static("image/andrews.png"),
        _k("D.G.Ruparel College"): static("image/d.g.ruparel.png"),
        _k("K.C College"): static("image/k.c.png"),
    }

    ui_colleges = []
    for c in colleges:
        key = _k(c.name)
        logo = logo_map.get(key, static("image/college-fallback.png"))
        ui_colleges.append(
            {
                "name": c.name,
                "location": c.location or "",
                "logo": logo,
                # Feel free to wire this to a filtered events page later:
                "href": "#",
            }
        )

    return render(
        request,
        "colleges/college_event_portal.html",
        {
            "colleges": ui_colleges,
        },
    )
