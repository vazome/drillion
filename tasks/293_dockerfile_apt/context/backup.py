"""Nightly backup: dump the database with pg_dump and upload the file over HTTPS.

pg_dump comes from the Debian package postgresql-client, and the upload needs the CA
certificates in ca-certificates. Neither is in a slim image."""

import os
import subprocess
import urllib.request

dump = subprocess.run(
    ["pg_dump", "--format=custom", os.environ["DATABASE_URL"]],
    check=True,
    capture_output=True,
).stdout
request = urllib.request.Request(os.environ["UPLOAD_URL"], data=dump, method="PUT")
urllib.request.urlopen(request, timeout=60)
