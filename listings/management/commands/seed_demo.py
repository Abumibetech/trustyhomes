from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from agents.models import AgentProfile
from listings.models import Property, State

DEMO_PROPERTIES = [
    {
        "title": "Cozy Self Contain near Wuse Market",
        "area": "Wuse II", "state": "FCT - Abuja", "type": "Self Contain",
        "price": 550000, "period": "yearly", "bedrooms": 1, "bathrooms": 1,
        "desc": "A neat, well-ventilated self-contain unit with tiled floors, running water, and 24-hour road access. Close to Wuse Market and major bus stops.",
        "verified": True, "featured": True,
    },
    {
        "title": "Modern 2 Bedroom Flat in Life Camp, Abuja",
        "area": "Life Camp", "state": "FCT - Abuja", "type": "2 Bedroom",
        "price": 1800000, "period": "yearly", "bedrooms": 2, "bathrooms": 2,
        "desc": "Newly built 2-bedroom flat with fitted kitchen, POP ceiling, ample parking space, and 24/7 security in a serene estate.",
        "verified": True, "featured": True,
    },
    {
        "title": "Luxury 3 Bedroom Terrace in Lekki, Lagos",
        "area": "Lekki", "state": "Lagos", "type": "3 Bedroom",
        "price": 6500000, "period": "yearly", "bedrooms": 3, "bathrooms": 4,
        "desc": "Executive 3-bedroom terrace duplex with BQ, fitted kitchen and estate power backup, minutes from the Lekki-Epe expressway.",
        "verified": True, "featured": True,
    },
    {
        "title": "Affordable 1 Bedroom Flat in Yaba, Lagos",
        "area": "Yaba", "state": "Lagos", "type": "1 Bedroom",
        "price": 900000, "period": "yearly", "bedrooms": 1, "bathrooms": 1,
        "desc": "Bright, airy 1-bedroom apartment close to Lagos's tech hub, walking distance to shopping and transport links.",
        "verified": True, "featured": False,
    },
    {
        "title": "Spacious 2 Bedroom in GRA Phase 2, Port Harcourt",
        "area": "GRA Phase 2", "state": "Rivers", "type": "2 Bedroom",
        "price": 1500000, "period": "yearly", "bedrooms": 2, "bathrooms": 2,
        "desc": "Well-maintained 2-bedroom flat in a quiet, secure GRA close, with good road network and constant water supply.",
        "verified": False, "featured": False,
    },
    {
        "title": "Modern Mini Flat in Bodija, Ibadan",
        "area": "Bodija", "state": "Oyo", "type": "Mini Flat",
        "price": 420000, "period": "yearly", "bedrooms": 1, "bathrooms": 1,
        "desc": "Budget-friendly mini flat ideal for a single tenant or young couple, close to Bodija Market and major schools.",
        "verified": True, "featured": False,
    },
]


class Command(BaseCommand):
    help = (
        "[DEV/DEMO ONLY] Creates a fake demo agent (username: demoagent) and 6 sample "
        "listings across Abuja, Lagos, Port Harcourt and Ibadan, so a local or staging "
        "copy of the site isn't empty. These listings have no photos attached (they'll "
        "show the normal 'Photos coming soon' placeholder) rather than relying on "
        "external image links that can break. Refuses to run when DEBUG=False (i.e. in "
        "production) unless you pass --force. For a real launch, use 'seed_locations' "
        "instead — it only adds real states/areas/property types, no fake accounts or "
        "listings."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow running even when DEBUG=False. Not recommended on a live production site.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "Refusing to seed fake demo data because DEBUG=False (this looks like "
                "production). Run 'python manage.py seed_locations' instead for real "
                "reference data, or re-run this with --force if you really want demo "
                "content here (e.g. a staging site)."
            )

        # Make sure the real states/areas/property types exist first.
        call_command("seed_locations")

        state_map = {s.name: s for s in State.objects.all()}

        user, created = User.objects.get_or_create(
            username="demoagent", defaults={"email": "demoagent@trustyhomes.local"}
        )
        if created:
            user.set_password("DemoAgent2026!")
            user.save()

        profile, _ = AgentProfile.objects.get_or_create(
            user=user,
            defaults={
                "business_name": "Zenith Homes Realty",
                "whatsapp_number": "2348012345678",
                "bio": "Trusted property agent with 6+ years of experience helping tenants find genuine homes across Nigeria.",
                "is_verified": True,
                "plan": AgentProfile.PLAN_PRO,
                "account_type": AgentProfile.ACCOUNT_TYPE_AGENT,
            },
        )

        created_count = 0
        for item in DEMO_PROPERTIES:
            if Property.objects.filter(title=item["title"]).exists():
                continue
            Property.objects.create(
                agent=profile,
                title=item["title"],
                description=item["desc"],
                property_type=item["type"],
                state=state_map[item["state"]],
                area=item["area"],
                price=item["price"],
                price_period=item["period"],
                bedrooms=item["bedrooms"],
                bathrooms=item["bathrooms"],
                is_verified=item["verified"],
                is_featured=item["featured"],
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. {created_count} demo properties created across 4 states. "
            f"Demo agent login -> username: demoagent / password: DemoAgent2026!"
        ))
