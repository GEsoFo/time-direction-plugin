import json,re,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from time_direction_mcp import server,backend,__version__
class PackageTest(unittest.TestCase):
    def test_manifest_skill_references_and_tool_binding(self):
        p=json.loads((ROOT/'plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(p['version'],__version__)
        new=json.loads((ROOT/'mcp.json').read_text(encoding='utf-8'))['mcpServers']
        old=json.loads((ROOT/'.mcp.json').read_text(encoding='utf-8'))['mcpServers']
        self.assertEqual(new['time-direction']['type'],'stdio')
        self.assertEqual(new['time-direction']['command'],old['time-direction']['command'])
        compat=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        for field in ['skills','mcpServers']:
            value=compat[field];self.assertTrue(value.startswith('./'));self.assertTrue((ROOT/value).exists())
        skill=ROOT/'skills/time-direction-election'
        text=(skill/'SKILL.md').read_text(encoding='utf-8')
        for name in re.findall(r'`((?:get_|build_|read_|render_)[a-z_]+)',text):self.assertIn(name,server.FUNCTIONS)
        for path in re.findall(r'\]\((references/[^)]+)\)',text):self.assertTrue((skill/path).is_file())
        self.assertIn('value: "time-direction"',(skill/'agents/openai.yaml').read_text(encoding='utf-8'))
    def test_configured_output_does_not_probe_unusable_system_temp(self):
        from unittest.mock import patch
        import os
        with patch.dict(os.environ,{'TIME_DIRECTION_OUTPUT_ROOT':str(ROOT/'test-output')}):
            with patch.object(backend.tempfile,'gettempdir',side_effect=OSError('unusable system temp')):
                self.assertEqual(backend.output_root(),(ROOT/'test-output').resolve())
    def test_specified_direction_survives_request_and_render(self):
        import os
        previous=os.environ.get('TIME_DIRECTION_OUTPUT_ROOT')
        with tempfile.TemporaryDirectory(prefix='plugin-direction-test-') as tmp:
            os.environ['TIME_DIRECTION_OUTPUT_ROOT']=tmp
            try:
                result=backend.build_election_request('2026-10-07',days=1,purpose='测试事项',participants=[{'name':'本人','branch':'午'}],mountain='酉')
                r=backend.read_election_windows(result['artifact_id'],limit=1)
                self.assertEqual(r['context']['mountain'],'酉')
                self.assertTrue(r['windows'][0]['target_relations'])
                review={'facts_digest':r['facts_digest'],'context':r['context'],'decisions':[{'id':r['windows'][0]['id'],'verdict':'待定','reason':'测试协议格式，不是实际择日判断。','evidence':['pillars.日']}]}
                result=backend.render_election_calendar(result['artifact_id'],review)
                self.assertEqual(result['reviewed_windows'],1)
                f=backend.get_direction_facts('2026-10-07T12:00:00+08:00',mountain='酉')
                self.assertEqual(f['context']['mountain'],'酉')
            finally:
                backend._stored_facts.cache_clear()
                if previous is None:os.environ.pop('TIME_DIRECTION_OUTPUT_ROOT',None)
                else:os.environ['TIME_DIRECTION_OUTPUT_ROOT']=previous
if __name__=='__main__':unittest.main()
