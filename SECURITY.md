# Privacy and release handling

The computation code makes no runtime network requests. Installing dependencies contacts the configured package index. Model clients receive the tool arguments and returned facts; their own data handling is outside this package.

Generated artifacts can contain names, natal branches, coordinates, purposes and model judgments. Calendar `.data.js` companions also contain these details, even when raw JSON files are not served. Keep the whole generated folder private unless you intend to share it. Preview URLs and aliases are local access capabilities, not user authentication; avoid predictable aliases for sensitive records. The preview listens on loopback, blocks cross-site fetches and sends a same-origin resource policy. It is not a multi-user security boundary. Close the MCP/preview process to stop serving files; output files persist until removed.

Publish only a reviewed release ZIP or the files in `release-files.json`. Do not upload an entire working directory, environment, output folder or older release archive. The release builder uses a fresh staging directory and checks both ZIP and wheel for common path/credential signatures and unwanted files. Automated scans cannot recognize every possible personal fact or secret; review additions to the file list and source examples before release.

To rebuild:

```sh
python -m unittest discover -s tests -v
python scripts/package_release.py
```

For security reports, privately contact the repository maintainer if a private reporting route is available. Do not post actual credentials, private artifacts, coordinates or preview tokens in public issues.
