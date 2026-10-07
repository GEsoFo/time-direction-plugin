"""Build from an explicit, reviewable file list in a fresh staging directory."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATTERNS = {
    'machine path': re.compile(r'(?i)(?:[a-z]:[\\/]+(?:users|code)[\\/]|/(?:home|Users)/)[^\s]+'),
    'conversation URL': re.compile(r'https://(?:chatgpt|chat.openai)\.com/c/[a-z0-9-]+', re.I),
    'credential': re.compile(r'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)'),
}


def audit_bytes(name, content):
    text = content.decode('utf-8', errors='replace')
    for label, pattern in PRIVATE_PATTERNS.items():
        if pattern.search(text):
            raise ValueError(f'Possible {label} in {name}; inspect locally before release')


def source_files(root=None):
    root = Path(root or ROOT).resolve()
    names = json.loads((root/'release-files.json').read_text(encoding='utf-8'))
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names) or len(names) != len(set(names)):
        raise ValueError('Release manifest must contain unique file names')
    files = []
    for name in names:
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe release manifest entry')
        path = root/name
        if not path.is_file() or root not in path.resolve().parents or any(p.is_symlink() for p in [path, *path.parents] if p != root):
            raise ValueError(f'Missing or linked release file: {name}')
        files.append(path)
    return files


def audit_archive(path):
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe archive entry')
            if any(p in {'.git','.venv','__pycache__','output','outputs'} for p in rel.parts) or rel.suffix in {'.pyc','.pyo','.pem','.key'} or rel.name.startswith('.env'):
                raise ValueError(f'Private or generated archive entry: {name}')
            audit_bytes(name, archive.read(name))


def main():
    output = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'dist'
    if output == ROOT or ROOT in output.parents and output != ROOT/'dist':
        raise ValueError('Output must be outside plugin source or its dist directory')
    output.mkdir(parents=True, exist_ok=True)
    version = json.loads((ROOT/'plugin.json').read_text(encoding='utf-8'))['version']
    files = source_files()
    with tempfile.TemporaryDirectory(prefix='time-direction-release-') as temporary:
        stage = Path(temporary)/'source'
        for path in files:
            relative = path.relative_to(ROOT)
            audit_bytes(relative, path.read_bytes())
            destination = stage/relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        resource = stage/'src/time_direction_mcp/resources/plugin'
        for path in [stage/'plugin.json',stage/'mcp.json',stage/'.mcp.json',stage/'.codex-plugin/plugin.json',*(stage/'skills').rglob('*')]:
            if path.is_file():
                destination = resource/path.relative_to(stage)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
        built = Path(temporary)/'built'
        subprocess.run([sys.executable,'-m','pip','wheel',str(stage),'--no-deps','--no-build-isolation','--wheel-dir',str(built)],check=True)
        archive = built/f'time-direction-plugin-{version}.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for path in files:
                rel = path.relative_to(ROOT)
                z.write(stage/rel,rel)
        wheel = built/f'time_direction_mcp-{version}-py3-none-any.whl'
        for path in [archive,wheel]:
            audit_archive(path)
        checks = output/f'SHA256SUMS-{version}.txt'
        for path in [archive,wheel]:
            shutil.copyfile(path,output/path.name)
        checks.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in [archive,wheel]),encoding='utf-8')
    print(json.dumps({'plugin_zip':str(output/archive.name),'wheel':str(output/wheel.name),'source_files':len(files),'privacy_scan':'passed'},ensure_ascii=False))


if __name__ == '__main__':
    main()
