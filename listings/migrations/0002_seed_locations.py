"""
Data migration: seeds real Nigerian states, neighbourhoods and property types.

This runs automatically as part of `python manage.py migrate` — on your laptop,
on a fresh production database, anywhere. That's on purpose: search filters
(state/area/property type dropdowns) need this data to exist or they render
empty, and a step that's easy to forget ("did you run the seed command?")
is a step that WILL be forgotten on launch day. This migration means it can't be.

Safe to run multiple times (get_or_create) and creates zero fake agents or
listings — only real reference data.
"""

from django.db import migrations

STATE_AREAS = {
    "FCT - Abuja": [
        "Wuse II", "Wuse", "Maitama", "Asokoro", "Garki", "Garki II", "Utako",
        "Jabi", "Life Camp", "Gwarinpa", "Kado", "Katampe", "Katampe Extension",
        "Wuye", "Lugbe", "Kubwa", "Nyanya", "Karu", "Apo", "Apo Dutse", "Gudu",
        "Dawaki", "Galadimawa", "Gwagwalada", "Idu", "Dei-Dei", "Jahi", "Duboyi",
        "Mabushi", "Karshi", "Kuje", "Bwari", "Dutse-Alhaji", "Byazhin",
        "Kabusa", "Lokogoma", "Games Village",
    ],
    "Lagos": [
        "Lekki", "Ikeja", "Yaba", "Ajah", "Surulere", "Victoria Island",
        "Ikoyi", "Magodo", "Gbagada", "Festac Town", "Ikorodu", "Ajao Estate",
        "Ogudu", "Ogba", "Alaba", "Ipaja", "Egbeda", "Isolo", "Maryland",
        "Ojota", "Oshodi", "Apapa", "Badagry", "Epe", "Ikotun",
    ],
    "Rivers": [
        "GRA Phase 1", "GRA Phase 2", "Old GRA", "Trans Amadi", "Rumuola",
        "Eliozu", "Woji", "Rumuokwuta", "D-Line", "Elelenwo", "Rumuigbo",
    ],
    "Oyo": ["Bodija", "Sango", "Akobo", "Ring Road", "Iwo Road", "Dugbe", "Apata", "Molete"],
    "Kaduna": ["Barnawa", "Malali", "Sabon Tasha", "Kawo", "Narayi", "Ungwan Rimi"],
    "Kano": ["Nassarawa GRA", "Sabon Gari", "Bompai", "Kabuga", "Zoo Road"],
    "Enugu": ["Independence Layout", "GRA", "New Haven", "Trans Ekulu", "Achara Layout"],
    "Delta": ["Effurun", "Warri GRA", "Asaba GRA", "Okpanam", "Enerhen"],
    "Edo": ["GRA Benin", "Ugbowo", "Sapele Road", "Airport Road", "Ekenwan"],
    "Anambra": ["Awka GRA", "Trans Nkisi (Onitsha)", "Fegge (Onitsha)", "Nnewi Road"],
    "Ogun": ["Sagamu Interchange", "Oke-Ilewo (Abeokuta)", "Mowe", "Ibafo", "Sango-Ota"],
    "Plateau": ["Rayfield (Jos)", "Anglo Jos", "Bukuru", "Tudun Wada (Jos)"],
    "Cross River": ["State Housing (Calabar)", "Federal Housing (Calabar)", "Marian Road"],
    "Akwa Ibom": ["Shelter Afrique (Uyo)", "Ewet Housing (Uyo)", "Osongama Estate"],
    "Abia": ["World Bank Housing (Umuahia)", "Aba GRA", "Ariaria (Aba)"],
    "Imo": ["New Owerri", "World Bank Housing (Owerri)", "Aladinma"],
    "Kwara": ["GRA Ilorin", "Tanke", "Fate Road"],
    "Bauchi": ["Yelwa", "Wunti", "Gwallameji"],
    "Benue": ["High Level (Makurdi)", "Wurukum", "North Bank"],
    "Borno": ["GRA Maiduguri", "Old GRA", "Gwange"],
    "Ebonyi": ["Abakaliki GRA", "Kpirikpiri"],
    "Ekiti": ["Ado GRA", "Basiri"],
    "Gombe": ["Pantami", "Jekadafari"],
    "Jigawa": ["Dutse GRA"],
    "Kebbi": ["Birnin Kebbi GRA"],
    "Kogi": ["Lokoja GRA", "Felele"],
    "Katsina": ["Katsina GRA"],
    "Nasarawa": ["Lafia GRA", "Karu (Nasarawa)"],
    "Niger": ["Minna GRA", "Tunga"],
    "Ondo": ["Alagbaka (Akure)", "Ijapo Estate"],
    "Osun": ["Osogbo GRA", "Ede Road"],
    "Sokoto": ["Sokoto GRA"],
    "Taraba": ["Jalingo GRA"],
    "Yobe": ["Damaturu GRA"],
    "Zamfara": ["Gusau GRA"],
    "Adamawa": ["Yola GRA", "Jimeta"],
}

PROPERTY_TYPES = [
    "Self Contain", "Mini Flat", "1 Bedroom", "2 Bedroom", "3 Bedroom",
    "4 Bedroom", "Duplex", "Terrace Duplex", "Detached House", "Shop / Office",
    "Land",
]


def seed_locations(apps, schema_editor):
    State = apps.get_model("listings", "State")
    Area = apps.get_model("listings", "Area")
    PropertyType = apps.get_model("listings", "PropertyType")

    for name in PROPERTY_TYPES:
        PropertyType.objects.get_or_create(name=name)

    for state_name, areas in STATE_AREAS.items():
        state, _ = State.objects.get_or_create(name=state_name)
        for area_name in areas:
            Area.objects.get_or_create(state=state, name=area_name)


def remove_seeded_locations(apps, schema_editor):
    # Intentionally a no-op: reversing this would delete real reference data
    # (and any properties/areas an agent has since attached to it).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_locations, remove_seeded_locations),
    ]
