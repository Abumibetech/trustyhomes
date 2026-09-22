Drop real photos here with these EXACT filenames to make them appear
automatically on the homepage's "Browse by city" section — no code
changes needed, just add the file and restart/redeploy:

  abuja.jpg
  lagos.jpg
  port-harcourt.jpg
  ibadan.jpg
  kano.jpg
  enugu.jpg

Recommended: roughly square photos (e.g. 800x800px), under 300KB each
so the homepage stays fast. Until a file is added, that city's card
shows a designed gradient + skyline icon instead — it will never show
a broken image icon.

If you deploy to Render (or anywhere using `collectstatic`), just make
sure these files are added to the repo BEFORE you push/deploy, so
`python manage.py collectstatic` picks them up.
