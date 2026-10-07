"""Loopback-only preview of explicitly registered election artifacts."""
import argparse,json,mimetypes,os,re,secrets,shutil,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit
from . import __version__

class PreviewService:
    def __init__(self,port=0):
        self.entries={};self.paths={};self.lock=threading.RLock()
        service=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_HEAD(self):self.respond(False)
            def do_GET(self):self.respond(True)
            def respond(self,body):
                host=self.headers.get('Host','').split(':')[0]
                if host not in ['127.0.0.1','localhost']:self.send_error(403);return
                if self.headers.get('Sec-Fetch-Site')=='cross-site':self.send_error(403);return
                route=unquote(urlsplit(self.path).path)
                if route=='/health':
                    data=json.dumps({'service':'time-direction-preview','version':__version__}).encode()
                    self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers()
                    if body:self.wfile.write(data)
                    return
                parts=route.strip('/').split('/')
                if len(parts)==3 and parts[0]=='c':key,name=parts[1:]
                elif len(parts)==2:key,name=parts
                else:self.send_error(404);return
                with service.lock:folder=service.entries.get(key)
                if folder is None:self.send_error(404);return
                if name=='index.html':name='择时日历.html'
                allowed=name=='择时日历.html' or bool(re.fullmatch(r'择时日历(?:\.\d{4}-\d{2})?\.data\.js',name))
                if not allowed:self.send_error(404);return
                path=folder/name
                if path.is_symlink() or path.resolve().parent!=folder or not path.is_file():self.send_error(404);return
                mime='text/html' if path.suffix=='.html' else 'text/javascript'
                self.send_response(200);self.send_header('Content-Type',mime+'; charset=utf-8');self.send_header('Content-Length',str(path.stat().st_size))
                self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('Cross-Origin-Resource-Policy','same-origin');self.end_headers()
                if body:
                    try:
                        with path.open('rb') as stream:shutil.copyfileobj(stream,self.wfile)
                    except (BrokenPipeError,ConnectionResetError):pass
        try:self.server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
        except OSError:
            if not port:raise
            self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.server.daemon_threads=True;self.port=self.server.server_port
        self.thread=threading.Thread(target=self.server.serve_forever,name='time-direction-preview',daemon=True);self.thread.start()
    def register(self,folder,alias=None):
        folder=Path(folder).resolve()
        if not (folder/'择时日历.html').is_file():raise ValueError('Calendar HTML not found')
        if alias is not None and (not isinstance(alias,str) or not re.fullmatch(r'[a-z0-9_-]{1,64}',alias)):raise ValueError('Invalid preview alias')
        with self.lock:
            if alias in self.entries and self.entries[alias]!=folder:raise ValueError('Preview alias is already registered')
            token=self.paths.get(str(folder))
            if token is None:
                record={}
                record_path=folder/'preview.json'
                if record_path.is_file():
                    try:record=json.loads(record_path.read_text(encoding='utf-8'))
                    except (ValueError,OSError):pass
                if not isinstance(record,dict):record={}
                token=record.get('token')
                if not isinstance(token,str) or not re.fullmatch(r'[0-9a-f]{32}',token):token=secrets.token_hex(16)
                while token in self.entries and self.entries[token]!=folder:token=secrets.token_hex(16)
                self.paths[str(folder)]=token;self.entries[token]=folder
                aliases=record.get('aliases',[])
                for name in aliases if isinstance(aliases,list) else []:
                    if isinstance(name,str) and re.fullmatch(r'[a-z0-9_-]{1,64}',name) and (name not in self.entries or self.entries[name]==folder):self.entries[name]=folder
            if alias:
                if not re.fullmatch(r'[a-z0-9_-]{1,64}',alias):raise ValueError('Invalid preview alias')
                self.entries[alias]=folder
            aliases=[name for name,value in self.entries.items() if value==folder and name!=token]
            record_path=folder/'preview.json';temporary=folder/'preview.json.tmp'
            temporary.write_text(json.dumps({'token':token,'aliases':aliases})+'\n',encoding='utf-8');temporary.replace(record_path)
        return f'http://127.0.0.1:{self.port}/c/{token}/index.html'
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)

_SERVICE=None
_LOCK=threading.RLock()
def calendar_url(folder):
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            port=int(os.environ.get('TIME_DIRECTION_PREVIEW_PORT','0'))
            if not 0<=port<=65535:raise ValueError('Preview port must be 0..65535')
            _SERVICE=PreviewService(port)
        return _SERVICE.register(folder)

def main():
    parser=argparse.ArgumentParser(description='Keep a generated calendar preview available while this process runs')
    parser.add_argument('--artifact',required=True);parser.add_argument('--output-root');parser.add_argument('--port',type=int,default=0);parser.add_argument('--alias')
    args=parser.parse_args()
    if args.output_root:os.environ['TIME_DIRECTION_OUTPUT_ROOT']=args.output_root
    from .backend import artifact_dir
    service=PreviewService(args.port)
    try:
        url=service.register(artifact_dir(args.artifact),args.alias)
        print(json.dumps({'preview_url':url,'port':service.port,'lifetime':'while this preview process is running'}),flush=True)
        service.thread.join()
    except KeyboardInterrupt:pass
    finally:service.close()
if __name__=='__main__':main()


def restore_registered(root):
    root=Path(root)
    if not root.is_dir():return 0
    restored=0
    for folder in root.iterdir():
        if re.fullmatch(r'[0-9a-f]{12}',folder.name) and folder.is_dir() and not folder.is_symlink() and (folder/'preview.json').is_file():
            try:calendar_url(folder);restored+=1
            except (ValueError,OSError):continue
    return restored
