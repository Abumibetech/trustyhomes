from django.core.management.base import BaseCommand

from listings.models import Area, PropertyType, State

# Real neighbourhoods/districts for Nigeria's biggest rental markets, plus
# every other state so search works nationwide from day one. Add more any
# time from /admin/listings/area/ — no code changes needed.
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


class Command(BaseCommand):
    help = (
        "Seeds real reference data (all 36 states + FCT, neighbourhoods, property "
        "types) so search works nationwide immediately. Safe to run in production — "
        "creates NO fake agents or listings."
    )

    def handle(self, *args, **options):
        pt_created = 0
        for name in PROPERTY_TYPES:
            _, created = PropertyType.objects.get_or_create(name=name)
            pt_created += int(created)

        area_created = 0
        state_created = 0
        for state_name, areas in STATE_AREAS.items():
            state, created = State.objects.get_or_create(name=state_name)
            state_created += int(created)
            for area_name in areas:
                _, created = Area.objects.get_or_create(state=state, name=area_name)
                area_created += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Done. {State.objects.count()} states/territories, {area_created} new "
            f"neighbourhoods, and {pt_created} new property types. No demo agents or "
            f"listings were created — this is real, production-safe reference data."
        ))
