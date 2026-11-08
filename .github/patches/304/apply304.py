#!/usr/bin/env python3
"""Rebuild the exact verified Chaosbuddy 3.0.4 source tree from the 3.1.0 CI ZIP.

The GitHub ZIP has the same original binary assets as 3.0.3. This text-only
compressed edit delta restores the 3.0.3 Java/manifest and applies 3.0.4 fixes.
NO signer backup, private keys, environment secrets, or other credentials.
"""
from pathlib import Path
import hashlib, base64, json, lzma, sys

project=Path.cwd()
here=Path(__file__).resolve().parent
chunks=[(here / ("part%d.b64" % i)).read_text(encoding="ascii").strip() for i in (1,2,3)]
encoded="".join(chunks)
assert len(encoded)==9840, "Missing or truncated patch chunk"
assert hashlib.sha256(encoded.encode("ascii")).hexdigest()=="925a2838a0030c5205b1d533cabcc5a64507e49dbb5d97799648e2f82738bf88", "Compressed patch SHA256 mismatch"
blob=lzma.decompress(base64.b64decode(encoded))
assert hashlib.sha256(blob).hexdigest()=="3b6966eeeb2f8df5a9617300a510e11e8755c02259691093ca56db83acb78359", "Decoded patch SHA256 mismatch"
changes=json.loads(blob.decode("utf-8"))
for name,old_digest,new_digest,ops in changes:
    path=project/name
    before=path.read_text(encoding="utf-8") if path.exists() else ""
    assert hashlib.sha256(before.encode("utf-8")).hexdigest().startswith(old_digest), f"Unexpected base content {name}"
    result=before
    for start,end,replacement in reversed(ops):
        assert 0<=start<=end<=len(before), f"Invalid edit range {name}"
        result=result[:start]+replacement+result[end:]
    assert hashlib.sha256(result.encode("utf-8")).hexdigest().startswith(new_digest), f"Unexpected target content {name}"
    if not result:
        path.unlink(missing_ok=True)
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(result,encoding="utf-8")
    print("Verified exact 3.0.4 source:",name)

# Debug preview installs next to the 3.0.3; NEVER sign as a fake in-place update.
gradle=project/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
assert g.count("applicationId 'de.boyka.kallebuddy'")==1
gradle.write_text(g.replace("applicationId 'de.boyka.kallebuddy'","applicationId 'de.boyka.kallebuddy.test304'"),encoding="utf-8")
manifest=project/"app/src/main/AndroidManifest.xml"
s=manifest.read_text(encoding="utf-8")
assert s.count("Kalle – Chaosbuddy 3.0.4")==2
manifest.write_text(s.replace("Kalle – Chaosbuddy 3.0.4","Kalle 3.0.4 Test"),encoding="utf-8")
print("Exact 3.0.4 source restored, with independent test package de.boyka.kallebuddy.test304.")
