import unittest,sys,json,subprocess,tempfile,os
from pathlib import Path
from datetime import datetime,timedelta

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from time_direction_mcp import backend
e=backend.engine()
from qimen import chart,pattern_matches,RING,STARS,DOORS,INSTRUMENTS,TERM_JU
from astronomy import positions_many,validate_observer

class QimenTest(unittest.TestCase):
    def test_primary_tiandun_examples(self):
        a=chart('乙丑','乙酉','冬至',4)
        b=chart('戊辰','庚申','夏至',6)
        hit=lambda q:[p['number'] for p in q['palaces'] if any(x['name']=='天遁' for x in p['patterns'])]
        self.assertEqual(hit(a),[1]);self.assertEqual(hit(b),[9])
        self.assertEqual((a['zhi_fu'],a['zhi_shi']),('天心','开门'))
        self.assertEqual((b['zhi_fu'],b['zhi_shi']),('天蓬','休门'))

    def test_all_1080_ju_hour_permutations(self):
        cycle=[e.GAN[i%10]+e.ZHI[i%12] for i in range(60)]
        for term in ['冬至','夏至']:
            for ju in range(1,10):
                for hour in cycle:
                    q=chart('甲子',hour,term,ju);outer=[p for p in q['palaces'] if p['number']!=5]
                    self.assertEqual(sorted(s for p in outer for s in p['heaven_stems']),sorted(INSTRUMENTS))
                    self.assertEqual(len({p['door'] for p in outer}),8)
                    self.assertEqual(len({p['god'] for p in outer}),8)
                    self.assertEqual(len([s for p in outer for s in p['stars']]),9)
                    self.assertEqual(next(p for p in outer if p['number']==q['zhi_fu_palace'])['god'],'值符')

    def test_yuan_and_primary_alternate_patterns(self):
        self.assertEqual(chart('甲子','甲子','冬至')['yuan'],'上元')
        self.assertEqual(chart('甲寅','甲子','冬至')['yuan'],'中元')
        self.assertEqual(chart('甲辰','甲子','冬至')['yuan'],'下元')
        p={'number':8,'heaven_stems':['乙'],'earth_stems':['辛'],'door':'休门','god':'九天'}
        names=lambda p:[x['name'] for x in pattern_matches(p)]
        self.assertIn('虎遁·艮休乙辛式',names(p));self.assertNotIn('虎遁·生乙辛另说',names(p))
        p['door']='生门';self.assertIn('虎遁·生乙辛另说',names(p));self.assertNotIn('虎遁·艮休乙辛式',names(p))
        p={'number':1,'heaven_stems':['乙'],'earth_stems':['戊'],'door':'休门','god':'九地'}
        self.assertIn('龙遁·坎休乙式',names(p))
        p['number']=3;self.assertNotIn('龙遁·坎休乙式',names(p))

    def test_exact_term_boundary(self):
        t=next(t for t,n in e.terms(2026) if n=='霜降')
        self.assertEqual(e.calc(t-timedelta(seconds=1))['qimen_chart']['solar_term'],'寒露')
        self.assertEqual(e.calc(t)['qimen_chart']['solar_term'],'霜降')

    def test_zhirun_continuity_leap_and_method_difference(self):
        from qimen import zhirun_schedule,CYCLE
        from lunar_python import Solar
        slots=zhirun_schedule(2026)
        for i,x in enumerate(slots):
            self.assertEqual((x['end']-x['start']).days,15)
            d=Solar.fromYmd(x['start'].year,x['start'].month,x['start'].day).getLunar().getDayInGanZhi()
            self.assertTrue(d[0] in '甲己' and d[1] in '子午卯酉')
            if i:self.assertEqual(slots[i-1]['end'],x['start'])
            if x['leap']:
                self.assertIn(x['term'],['芒种','大雪']);self.assertGreaterEqual(x['lead_days'],8)
                self.assertEqual(slots[i-1]['term'],x['term'])
        f=e.calc(datetime(2026,10,7,12))
        self.assertEqual(f['qimen_variants']['chaibu']['solar_term'],'秋分')
        self.assertEqual(f['qimen_variants']['zhirun']['solar_term'],'寒露')
        self.assertNotEqual(f['qimen_variants']['chaibu']['ju'],f['qimen_variants']['zhirun']['ju'])
        leap=next(x for x in slots if x['leap'] and x['start'].year>=2020)
        for offset,yuan in [(0,'上元'),(5,'中元'),(10,'下元')]:
            q=e.calc(leap['start']+timedelta(days=offset,hours=12),qimen_method='zhirun')['qimen_chart']
            self.assertTrue(q['timing']['is_leap']);self.assertEqual(q['yuan'],yuan);self.assertEqual(q['solar_term'],leap['term'])
        a=e.calc(datetime(2026,10,6,23,30),qimen_method='zhirun')['qimen_chart']
        b=e.calc(datetime(2026,10,7,0,30),qimen_method='zhirun')['qimen_chart']
        self.assertEqual(a,b)
        with self.assertRaises(ValueError):e.calc(datetime(2026,10,7),qimen_method='invalid')


class AstronomyTest(unittest.TestCase):
    def test_missing_observer_and_two_hemispheres(self):
        dt=datetime(2026,10,6,22)
        self.assertEqual(positions_many([dt],None)[0]['status'],'needs_observer')
        north=positions_many([dt],{'latitude':70,'longitude':0})[0]
        south=positions_many([dt],{'latitude':-70,'longitude':0})[0]
        self.assertEqual(len(north['stars']),7)
        self.assertTrue(all(s['above_horizon'] for s in north['stars']))
        self.assertTrue(all(not s['above_horizon'] for s in south['stars']))
        for s in north['stars']+south['stars']:
            self.assertTrue(0<=s['azimuth_deg']<360);self.assertTrue(-90<=s['altitude_deg']<=90)
        with self.assertRaises(ValueError):validate_observer({'latitude':91,'longitude':0})
        with self.assertRaises(ValueError):validate_observer({'latitude':True,'longitude':0})

    def test_location_and_clock_really_change_positions(self):
        dt=datetime(2026,10,6,22)
        a=positions_many([dt,dt+timedelta(hours=2)],{'latitude':30,'longitude':120})
        b=positions_many([dt],{'latitude':30,'longitude':0})
        self.assertNotEqual(a[0]['stars'][0]['azimuth_deg'],a[1]['stars'][0]['azimuth_deg'])
        self.assertNotEqual(a[0]['stars'][0]['azimuth_deg'],b[0]['stars'][0]['azimuth_deg'])

class MCPTest(unittest.TestCase):
    def test_real_stdio_handshake_tools_and_calls(self):
        packets=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},
                 {'jsonrpc':'2.0','method':'notifications/initialized'},
                 {'jsonrpc':'2.0','id':2,'method':'tools/list'},
                 {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'get_qimen_chart','arguments':{'datetime':'2026-10-06T20:00:00+08:00'}}},
                 {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'get_beidou_sky','arguments':{'datetime':'2026-10-06T20:00:00+08:00','observer':{'latitude':30,'longitude':120}}}}]
        r=subprocess.run([sys.executable,str(ROOT/'server.py')],input='\n'.join(json.dumps(x) for x in packets)+'\n',text=True,capture_output=True,encoding='utf-8',check=True)
        responses=[json.loads(x) for x in r.stdout.splitlines()]
        self.assertEqual(len(responses),4);self.assertEqual(responses[0]['result']['serverInfo']['name'],'time-direction-mcp')
        self.assertEqual(len(responses[1]['result']['tools']),8)
        self.assertFalse(responses[2]['result']['isError']);self.assertEqual(len(responses[2]['result']['structuredContent']['palaces']),9)
        self.assertFalse(responses[3]['result']['isError']);self.assertEqual(len(responses[3]['result']['structuredContent']['stars']),7)

    def test_joint_candidates_and_cross_month_artifact(self):
        f=backend.get_direction_facts('2026-10-06T20:00:00+08:00',qimen_method='zhirun',participants=[{'name':'甲方','branch':'午'},{'name':'乙方','branch':'酉'}])
        self.assertEqual(f['facts']['qimen_chart']['method_key'],'zhirun')
        self.assertEqual(len(f['direction_candidates']),12)
        self.assertIn('qimen',f['direction_candidates'][0]);self.assertEqual(len(f['direction_candidates'][0]['participants']),2)
        self.assertEqual(f['facts']['direction_systems']['real_beidou']['status'],'needs_observer')
        self.assertTrue(f['facts']['direction_systems']['liuren_noble']['ground_in_day_void'] in [True,False])
        with tempfile.TemporaryDirectory(prefix='time-direction-test-') as tmp:
            previous=os.environ.get('TIME_DIRECTION_OUTPUT_ROOT');os.environ['TIME_DIRECTION_OUTPUT_ROOT']=tmp
            try:
                result=backend.build_election_request('2026-10-30',days=4,purpose='一般事项',qimen_method='zhirun')
                request=json.loads(Path(result['request_path']).read_text(encoding='utf-8'))
                self.assertEqual(request['context']['qimen_method'],'zhirun')
                self.assertTrue(all(w['facts']['qimen_chart']['method_key']=='zhirun' for w in request['windows']))
                dates={w['id'][:10] for w in request['windows']}
                self.assertEqual(dates,{'2026-10-30','2026-10-31','2026-11-01','2026-11-02'})
                review={'facts_digest':request['facts_digest'],'context':request['context'],
                        'decisions':[{'id':w['id'],'verdict':'待定','reason':'测试格式，无指定事项个体裁决。','evidence':['pillars.日']} for w in request['windows']]}
                rendered=backend.render_election_calendar(result['artifact_id'],review)
                self.assertTrue(rendered['complete']);self.assertTrue(Path(rendered['html_path']).exists())
                with self.assertRaises(ValueError):backend.artifact_dir('../escape')
            finally:
                if previous is None:os.environ.pop('TIME_DIRECTION_OUTPUT_ROOT',None)
                else:os.environ['TIME_DIRECTION_OUTPUT_ROOT']=previous

    def test_full_leap_year_lazy_months_and_accumulating_reviews(self):
        with tempfile.TemporaryDirectory(prefix='time-direction-year-test-') as tmp:
            previous=os.environ.get('TIME_DIRECTION_OUTPUT_ROOT');os.environ['TIME_DIRECTION_OUTPUT_ROOT']=tmp
            try:
                result=backend.build_year_election(2028,purpose='年度事项',qimen_method='zhirun')
                self.assertEqual(result['days'],366);self.assertEqual(result['months'],12)
                folder=Path(result['html_path']).parent
                index=json.loads((folder/'request.json').read_text(encoding='utf-8'))
                self.assertTrue(index['window_index_only']);self.assertLess((folder/'request.json').stat().st_size,2_000_000)
                self.assertIn('2028-02-29',{w['id'][:10] for w in index['windows']})
                self.assertEqual(len(list(folder.glob('择时日历.2028-*.data.js'))),12)
                self.assertLess((folder/'择时日历.data.js').stat().st_size,2_000_000)
                boundary=next(i for i,w in enumerate(index['windows']) if w['id'].startswith('2028-02-01'))
                read=backend.read_election_windows(result['artifact_id'],offset=boundary-1,limit=2)
                self.assertEqual({w['id'][:7] for w in read['windows']},{'2028-01','2028-02'})
                self.assertTrue(all(w['facts']['qimen_chart']['method_key']=='zhirun' for w in read['windows']))
                self.assertEqual(read['next_offset'],boundary+1)
                month_mtimes={p.name:p.stat().st_mtime_ns for p in folder.glob('择时日历.2028-*.data.js')}
                for i,w in enumerate(read['windows']):
                    review={'facts_digest':result['facts_digest'],'context':result['context'],
                            'decisions':[{'id':w['id'],'verdict':'待定','reason':'测试格式，尚未实际判断。','evidence':['pillars.日']}]}
                    rendered=backend.render_election_calendar(result['artifact_id'],review)
                    self.assertEqual(rendered['reviewed_windows'],i+1);self.assertFalse(rendered['complete'])
                self.assertEqual(month_mtimes,{p.name:p.stat().st_mtime_ns for p in folder.glob('择时日历.2028-*.data.js')})
                wrong={**review,'context':{**review['context'],'qimen_method':'chaibu'}}
                with self.assertRaises(ValueError):backend.render_election_calendar(result['artifact_id'],wrong)
                end=backend.read_election_windows(result['artifact_id'],offset=result['window_count']-1,limit=14)
                self.assertEqual(len(end['windows']),1);self.assertFalse(end['has_more'])
                empty=backend.read_election_windows(result['artifact_id'],offset=result['window_count'],limit=7)
                self.assertEqual(empty['windows'],[]);self.assertFalse(empty['has_more'])
            finally:
                backend._stored_facts.cache_clear()
                if previous is None:os.environ.pop('TIME_DIRECTION_OUTPUT_ROOT',None)
                else:os.environ['TIME_DIRECTION_OUTPUT_ROOT']=previous


if __name__=='__main__':unittest.main()
