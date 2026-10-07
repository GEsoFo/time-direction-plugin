"""Release privacy and fresh-process regression tests using synthetic fixtures."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from time_direction_mcp import backend
from time_direction_mcp.preview import PreviewService, restore_registered
spec = importlib.util.spec_from_file_location('release_builder', ROOT/'scripts/package_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseSecurityTest(unittest.TestCase):
    def test_allowlist_excludes_unlisted_private_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'release-files.json').write_text('["README.md"]')
            (root/'README.md').write_text('public')
            for name in ['.env.local','notes.txt','facts.json','preview.json']:
                (root/name).write_text('synthetic private fixture')
            self.assertEqual([p.name for p in release.source_files(root)], ['README.md'])
            (root/'release-files.json').write_text('["../outside"]')
            with self.assertRaises(ValueError):release.source_files(root)

    def test_privacy_signatures_and_packaged_sources(self):
        fixtures = ['C:' + '/' + 'Users' + '/' + 'example/private', 'D:' + '\\code\\' + 'example',
                    'https://' + 'chatgpt.com/' + 'c/' + '12345678-abcd', 'sk-' + 'x'*30]
        for fixture in fixtures:
            with self.subTest(fixture=fixture[:3]), self.assertRaises(ValueError):
                release.audit_bytes('synthetic-fixture', fixture.encode())
        for path in release.source_files():release.audit_bytes(path.name,path.read_bytes())

    def test_invalid_profile_rejected_before_build(self):
        e = backend.engine()
        with patch.object(e,'build',side_effect=AssertionError('must not calculate')):
            for kwargs in [{'rollover':'bad'},{'noble_profile':'bad'},{'mountain':'bad'},{'qimen_method':'bad'}]:
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    backend.build_election_request('2026-10-01',**kwargs)
            with self.assertRaises(ValueError):backend.build_election_request('2099-12-31',days=2)
        with self.assertRaises(ValueError):backend.parse_time('2099-12-31T23:59:00-12:00')

    def test_fresh_process_reads_lazy_request_and_initial_context(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,{'TIME_DIRECTION_OUTPUT_ROOT':tmp}):
            result=backend.build_election_request('2026-10-01',days=1,purpose='示例事项',participants=[{'name':'示例参与者','branch':'子'}],mountain='酉',noble_profile='xieji')
            folder=Path(result['request_path']).parent
            data_script=(folder/'择时日历.data.js').read_text(encoding='utf-8')
            self.assertIn('"initial_context":',data_script)
            self.assertIn('示例参与者',data_script)
            request=json.loads((folder/'request.json').read_text(encoding='utf-8'))
            request['windows']=[{k:w[k] for k in ['id','start','end']} for w in request['windows']]
            request['window_index_only']=True
            (folder/'request.json').write_text(json.dumps(request),encoding='utf-8')
            env={**os.environ,'PYTHONPATH':str(ROOT/'src')}
            code="from time_direction_mcp import backend; import sys; r=backend.read_election_windows(sys.argv[1],limit=1); assert 'facts' in r['windows'][0]"
            run=subprocess.run([sys.executable,'-c',code,result['artifact_id']],env=env,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(run.returncode,0,run.stderr)
            backend._stored_facts.cache_clear()

    def test_corrupt_preview_records_do_not_break_restore(self):
        for record in ['[]','null','{"aliases":null}','{"aliases":42}']:
            with self.subTest(record=record), tempfile.TemporaryDirectory() as tmp:
                folder=Path(tmp)/'012345abcdef';folder.mkdir()
                (folder/'择时日历.html').write_text('example')
                (folder/'preview.json').write_text(record)
                service=PreviewService()
                try:
                    with patch('time_direction_mcp.preview.calendar_url',side_effect=service.register):
                        self.assertEqual(restore_registered(tmp),1)
                    self.assertRegex(json.loads((folder/'preview.json').read_text())['token'],r'^[a-f0-9]{32}$')
                finally:service.close()

    def test_alias_and_token_collision_cannot_replace_other_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            folders=[Path(tmp)/str(i) for i in range(2)]
            service=PreviewService()
            try:
                for folder in folders:
                    folder.mkdir();(folder/'择时日历.html').write_text(folder.name)
                    (folder/'preview.json').write_text(json.dumps({'token':'a'*32,'aliases':['example-calendar']}))
                first=service.register(folders[0]);second=service.register(folders[1])
                self.assertNotEqual(first,second)
                with urllib.request.urlopen(first) as response:self.assertEqual(response.read(),b'0')
                with self.assertRaises(ValueError):service.register(folders[1],alias='example-calendar')
            finally:service.close()

    def test_preview_rejects_cross_site_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);(folder/'择时日历.html').write_text('example')
            (folder/'择时日历.data.js').write_text('globalThis.LIUREN_CALENDAR_REVIEW={};')
            service=PreviewService()
            try:
                url=service.register(folder)
                with urllib.request.urlopen(url) as response:
                    self.assertEqual(response.headers['Cross-Origin-Resource-Policy'],'same-origin')
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(urllib.request.Request(url,headers={'Sec-Fetch-Site':'cross-site'}))
                self.assertEqual(error.exception.code,403);error.exception.close()
            finally:service.close()


if __name__=='__main__':unittest.main()
