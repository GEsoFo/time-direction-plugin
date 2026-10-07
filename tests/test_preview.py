import json,os,socket,tempfile,unittest,urllib.request,urllib.error
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from time_direction_mcp.preview import PreviewService
from time_direction_mcp import backend
class PreviewTest(unittest.TestCase):
    def test_calendar_assets_health_alias_and_boundaries(self):
        with tempfile.TemporaryDirectory(prefix='preview-check-') as tmp:
            folder=Path(tmp);(folder/'择时日历.html').write_text('<h1>日历</h1>',encoding='utf-8');(folder/'择时日历.data.js').write_text('window.DATA={};',encoding='utf-8');(folder/'facts.json').write_text('{"private":"not served"}',encoding='utf-8')
            s=PreviewService()
            try:
                url=s.register(folder,alias='example-calendar')
                self.assertEqual(url,s.register(folder));self.assertTrue(url.isascii())
                r=urllib.request.urlopen(url);self.assertEqual(r.status,200);self.assertIn('no-store',r.headers['Cache-Control']);self.assertIn('日历',r.read().decode())
                base=url.rsplit('/',1)[0]+'/'
                self.assertEqual(urllib.request.urlopen(base+'%E6%8B%A9%E6%97%B6%E6%97%A5%E5%8E%86.data.js').status,200)
                self.assertEqual(urllib.request.urlopen(f'http://127.0.0.1:{s.port}/example-calendar/index.html').status,200)
                health=json.load(urllib.request.urlopen(f'http://127.0.0.1:{s.port}/health'));self.assertEqual(health['service'],'time-direction-preview')
                for suffix in ['facts.json','../../config.toml','%2e%2e/config.toml','missing.data.js']:
                    with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(base+suffix)
                with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(urllib.request.Request(url,headers={'Host':'evil.example'}))
                with self.assertRaises(ValueError):s.register(folder,alias='../bad')
            finally:s.close()
    def test_restart_keeps_token_and_bookmark_alias(self):
        with tempfile.TemporaryDirectory(prefix='preview-restart-') as tmp:
            folder=Path(tmp);(folder/'择时日历.html').write_text('ok',encoding='utf-8')
            first=PreviewService();url=first.register(folder,alias='example-calendar');token=url.split('/')[-2];first.close()
            second=PreviewService()
            try:
                again=second.register(folder);self.assertEqual(again.split('/')[-2],token)
                self.assertEqual(urllib.request.urlopen(f'http://127.0.0.1:{second.port}/example-calendar/index.html').read(),b'ok')
                with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(again.replace('index.html','preview.json'))
                error.exception.close()
            finally:second.close()
    def test_port_conflict_falls_back_and_preview_failure_preserves_file(self):
        from unittest.mock import patch
        sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen();port=sock.getsockname()[1]
        s=PreviewService(port)
        try:self.assertNotEqual(s.port,port)
        finally:s.close();sock.close()
        with patch('time_direction_mcp.preview.calendar_url',side_effect=OSError('port unavailable')):
            result=backend._preview_fields(Path('.'));self.assertIn('preview_error',result);self.assertIn('html_path',result['preview_fallback'])
if __name__=='__main__':unittest.main()
