# TrustyHomes 🏠

**A property marketplace that connects owners and agents directly with people looking for a place — houses, land, offices, shortlets, shops, warehouses and more, across all 36 Nigerian states + FCT.**

TrustyHomes doesn't inspect or manage properties — it's the marketplace and
the traffic. An agent or owner posts a listing; a tenant finds it and
contacts them directly on WhatsApp or by phone. Admin never has to approve
a listing before it goes live — it's public the second it's posted. The
platform's protection comes from an easy report button on every listing,
reviewed by admins, plus an optional "Verified" badge admins can award
after checking an agent's identity (a signal, never a guarantee).

Everything is **free to use right now** while the platform is launching.
Agent plan limits (Free / Basic / Pro / Business) and "featured listing"
already exist in the data model so you can switch on real pricing later
without rebuilding anything — for now, upgrades happen manually: an agent
taps "Request this plan" on the Upgrade page, it opens WhatsApp with a
pre-filled message to you, and you flip their plan (or a property's
"Featured" flag) in `/admin/`.

---

## ✨ Features

**For tenants**
- Search nationwide: by category → state → neighbourhood → property type →
  budget, plus a free-text keyword search (title, description, area, state)
- 8 categories out of the box: House/Apartment for Rent, Short-let,
  Roommate/Shared Apartment, Office Space, Land, Shop, Warehouse, and
  Other Commercial Property
- "Browse by city" and "Browse by category" shortcuts on the homepage
- Photo galleries, optional YouTube video walkthrough, a facilities list,
  and an embedded map for every listing
- One-tap **WhatsApp contact** and **Call Agent** buttons — no forced
  in-site messaging
- **Share** any listing (native share sheet, or copies the link)
- **Comment on any listing** — public Q&A thread with like/upvote, right on
  the listing page
- **In-site messaging** — a real message thread with the agent (separate
  from WhatsApp), auto-refreshing every few seconds for a live feel, with
  an inbox and unread badges. All stored permanently in the database —
  nothing here is temporary or clears itself out.
- **Request an inspection** — a simple form the agent sees on their dashboard
- **Report a suspicious listing** — reviewed by admins, who can hide a
  listing in one click straight from the report
- **Favourites** (save listings) and **agent reviews/ratings**
- **Notifications** (inspection replies, new reviews, plan updates)
- Separate **tenant** and **agent/owner** sign-up flows
- **Forgot password** self-service reset via email

**For agents / property owners / real estate companies**
- Free plan: 50 uploads/day. Basic: 150/day. Pro: unlimited + featured.
  Business: custom, for large real estate companies — all free for now,
  upgrade by request
- Post any category — not just rentals — with category-aware forms (no
  pointless "bedrooms" field when listing land or a warehouse)
- A free-text "facilities" field per listing (water, 24hr electricity,
  parking, security, etc.)
- Multi-photo upload straight from the dashboard (drag in up to 8 photos
  per listing)
- Location picker: an interactive drag-a-pin map (OpenStreetMap/Leaflet —
  free forever, no API key, bundled locally so it never depends on a CDN)
  with free address search, plus a one-tap "use my current location" button
- State is a fixed dropdown (36 states + FCT); neighbourhood and property
  type are free-text with autocomplete that gets smarter as more agents use
  the platform — nothing is ever blocked by a missing dropdown option
- Dashboard: manage listings, see views, hide/show, edit, delete
- Public agent profile page with reviews & rating

**Monetization already wired into the data model**
- Agent plans (Free/Basic/Pro/Business) with daily upload limits
- Featured listings (`Property.is_featured` / `featured_until`)
- **Banner ads** (`Advertisement` model) — sell space to furniture
  companies, movers, mortgage providers, interior designers, etc. Placed on
  the homepage, above search results, or in a listing's sidebar; fully
  admin-managed with date ranges and click tracking. No payment gateway is
  wired up yet — advertisers pay you directly (bank transfer, invoice, etc.)
  and you flip `is_active` in `/admin/`.

**Admin**
- A custom **Admin Dashboard** (`/admin-dashboard/`, staff only, not linked
  in the site navigation — reach it directly by URL) with platform-wide
  stats: agents by plan, verified counts, pending inspections, unresolved
  reports, recent listings
- Full Django admin (`/admin/`) with one-click actions: verify/unverify
  agents, verify/feature properties, resolve reports (with a "hide this
  listing" action), update inspection status, manage banner ads

---

## 🗂 Project layout

```
trustyhomes/
├── core/          → home page, "how it works", admin dashboard
├── accounts/      → tenant & agent sign-up, login/logout, password reset
├── agents/        → agent profile, dashboard, add/edit listings, upgrade page
├── listings/      → properties, states/areas, favourites, reviews, reports,
│                    inspection requests, the location seed commands
├── notifications/ → in-app notification bell
├── templates/      → all HTML (inline CSS per template via {% block extra_css %})
└── static/         → static assets (empty by default — CSS lives inline)
```

---

## 🚀 Run it locally

Requires Python 3.11+ and pip.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser

# `migrate` already seeded real states/areas/property types for you (all 36
# states + FCT) — search filters work immediately, nothing else to run.

# OPTIONAL, local/staging only: adds a fake demo agent + 6 sample listings
# with stock photos so the site isn't empty while you're building. This
# command refuses to run in production (DEBUG=False) unless you pass --force.
python manage.py seed_demo

python manage.py runserver
```

Visit **http://127.0.0.1:8000/**. Admin is at **http://127.0.0.1:8000/admin/**
and the custom stats dashboard at **http://127.0.0.1:8000/admin-dashboard/**
(log in as a staff user first).

### Environment variables

See `.env.example` for the full list with explanations. Nothing there is
required for local development — sensible defaults kick in automatically
(SQLite database, console email backend, local-disk photo storage, no
Google Maps key needed — maps use free OpenStreetMap/Leaflet).

---

## ☁️ Deploy to Render (production)

This repo is ready for [Render](https://render.com)'s "Blueprint" flow:

1. Push this project to a GitHub/GitLab repo.
2. In Render, click **New → Blueprint**, point it at the repo — it reads
   `render.yaml` and sets up both a **free PostgreSQL database** and a
   **free web service** automatically, with `SECRET_KEY` generated and
   `DATABASE_URL` wired up for you.
3. In the web service's **Environment** tab, set:
   - `SITE_WHATSAPP_NUMBER` — your real WhatsApp number, digits only, with country code
   - `CLOUDINARY_URL` — see below, **do this before real agents upload real photos**
   - `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` — so password
     reset emails actually get delivered (otherwise they just log to Render's
     console)
4. Once deployed, open a **Shell** on the service and run:
   ```bash
   python manage.py createsuperuser
   ```
   (`migrate` — which Render already runs for you via `build.sh` /
   `Procfile`'s `release` step — auto-seeds real states/areas/property types,
   so there's nothing else to run.) Do **not** run `seed_demo` in production
   (it refuses to run unless you pass `--force`, and you shouldn't need to).

**No Blueprint? Manual setup works too:**
- Create a new **Web Service**, connect the repo.
- Build command: `./build.sh`
- Start command: `gunicorn trustyhomes.wsgi:application --bind 0.0.0.0:$PORT`
- Add a **PostgreSQL** instance and copy its "Internal Database URL" into
  the web service's `DATABASE_URL` environment variable.
- Set `SECRET_KEY` (any long random string), `DEBUG=False`, and
  `ALLOWED_HOSTS=.onrender.com` (or your real domain once you add one).

### ⚠️ Before real agents upload real photos: set up Cloudinary

Render's free/starter web services use an **ephemeral filesystem** —
anything an agent uploads (property photos, profile pictures) will be
**wiped on every redeploy or restart** unless you configure persistent
storage. This project already has [Cloudinary](https://cloudinary.com)
wired in and ready — it switches on automatically the moment you set the
`CLOUDINARY_URL` environment variable:

1. Create a free Cloudinary account.
2. From your Cloudinary dashboard, copy the value labelled "API Environment
   variable" (looks like `cloudinary://<api_key>:<api_secret>@<cloud_name>`).
3. Set it as `CLOUDINARY_URL` in Render's Environment tab and redeploy.

That's it — no code changes needed, `settings.py` detects it and switches
`MEDIA` storage to Cloudinary automatically. Until it's set, agents can
still paste an image **link** instead of uploading a file — every
`PropertyImage` has an `external_image_url` fallback field for exactly this.

### 🔒 Production security

`settings.py` automatically turns on HTTPS redirect, secure cookies, HSTS,
and clickjacking/MIME-sniffing protection whenever `DEBUG=False` — nothing
to configure beyond setting a real `SECRET_KEY` and `ALLOWED_HOSTS`. Run
`python manage.py check --deploy` any time to double-check your config.

---

## 💰 Turning pricing back on later

Nothing needs to be rebuilt. When you're ready to actually charge:

1. Add a payment provider (Paystack, Flutterwave, etc.) — the
   `AgentProfile.plan` / `plan_expires_on` and `Property.is_featured` /
   `featured_until` fields are already there, ready for a payment webhook
   to flip them automatically instead of an admin doing it by hand.
2. Update the copy on `templates/agents/upgrade.html` (it currently says
   "free during launch, request via WhatsApp").
3. Everything else — plan limits, the upgrade page's plan cards, featured
   badges on listings — already works.

---

## 🔒 Trust & safety notes

- "Verified" badges (on agents and on properties) are **admin-only** flags.
  Nothing marks itself verified — your team decides after checking ID,
  CAC, and/or a physical or photo inspection.
- Every property page has a **Report** button; reports land in
  `/admin/listings/report/` and on the Admin Dashboard.
- Reviews are one-per-tenant-per-agent (a second review updates the first,
  it doesn't duplicate).

---

## ✅ Pre-launch checklist

- [ ] `SECRET_KEY` set to a real, long random value (not the dev default)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` set to your real domain(s)
- [ ] `DATABASE_URL` pointing at PostgreSQL (not SQLite)
- [ ] `CLOUDINARY_URL` set, so uploaded photos persist
- [ ] `EMAIL_HOST` etc. set, so password resets actually arrive
- [ ] `SITE_WHATSAPP_NUMBER` set to your real business WhatsApp number
- [ ] `python manage.py migrate` run once (this also auto-seeds real states/
      areas/property types — no separate step needed)
- [ ] `python manage.py createsuperuser` run, and you've logged into `/admin/`

Made for Nigeria 🇳🇬 — built to earn trust, not just list houses.
