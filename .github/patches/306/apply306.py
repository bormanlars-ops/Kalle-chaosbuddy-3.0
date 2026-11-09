#!/usr/bin/env python3
"""Apply Kalle 3.0.6 to the 3.0.4 GitHub CI bootstrap; no signing secrets."""
from pathlib import Path
import base64, hashlib, json, lzma

root=Path.cwd()
gradle=root/"app/build.gradle"
manifest=root/"app/src/main/AndroidManifest.xml"
g=gradle.read_text(encoding="utf-8")
if "applicationId 'de.boyka.kallebuddy.test304'" in g:
    gradle.write_text(g.replace("applicationId 'de.boyka.kallebuddy.test304'", "applicationId 'de.boyka.kallebuddy'"),encoding="utf-8")
m=manifest.read_text(encoding="utf-8")
if "Kalle 3.0.4 Test" in m:
    manifest.write_text(m.replace("Kalle 3.0.4 Test", "Kalle – Chaosbuddy 3.0.4"),encoding="utf-8")

packed=(Path(__file__).parent/"kalle306-delta.b64").read_text(encoding="ascii")
changes=json.loads(lzma.decompress(base64.b64decode(packed)))
for name,before_sha,after_sha,edits in changes:
    p=root/name
    before=p.read_text(encoding="utf-8") if p.exists() else ""
    digest=hashlib.sha256(before.encode("utf-8")).hexdigest()
    if digest!=before_sha:
        raise RuntimeError("Source mismatch for %s: expected %s found %s" % (name,before_sha,digest))
    after=before
    for start,end,replacement in reversed(edits):
        assert 0<=start<=end<=len(before),name
        after=after[:start]+replacement+after[end:]
    assert hashlib.sha256(after.encode("utf-8")).hexdigest()==after_sha, name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(after,encoding="utf-8")
    print("Verified 3.0.6 source:",name)

# Never install the GitHub debug-signed artifact over the user's release-signed app.
g=gradle.read_text(encoding="utf-8")
assert g.count("applicationId 'de.boyka.kallebuddy'")==1
gradle.write_text(g.replace("applicationId 'de.boyka.kallebuddy'",
                            "applicationId 'de.boyka.kallebuddy.test306'"),encoding="utf-8")
m=manifest.read_text(encoding="utf-8")
assert "Kalle – Chaosbuddy 3.0.6" in m
manifest.write_text(m.replace("Kalle – Chaosbuddy 3.0.6","Kalle Chaosbuddy 3.0.6 TEST"),encoding="utf-8")
print("Configured safe standalone test package de.boyka.kallebuddy.test306")
