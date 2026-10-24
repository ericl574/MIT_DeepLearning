#!/usr/bin/env python3
"""Download publicly hosted Porter Robinson MIDI transcriptions from BitMidi.

Usage: python download_porter_midis.py
Run at the MIT_DeepLearning repository root to create data/midi/.
Respect site terms and artists' rights; do not commit third-party MIDI files.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re
import time

SONGS = [
    'Divinity', 'Fellow Feeling', 'Flicker', 'Fresh Static Snow',
    'Goodbye To A World', 'Hear The Bells', 'Lionhearted', 'Natural Light',
    'Polygon Dust', 'Sad Machine', 'Sea Of Voices', 'Unison', 'Years Of War'
]
BASE = 'https://bitmidi.com'
OUT = Path('data/midi')
OUT.mkdir(parents=True, exist_ok=True)

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', ('porter robinson ' + name).lower()).strip('-') + '-mid'

def fetch(url):
    req = Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; educational MIDI downloader)'})
    with urlopen(req, timeout=25) as response:
        return response.read()

def main():
    successes = 0
    for title in SONGS:
        slug = slugify(title)
        page = f'{BASE}/{slug}'
        dst = OUT / (slug[:-4] + '.mid')
        if dst.exists() and dst.read_bytes()[:4] == b'MThd':
            print(f'SKIP {dst}')
            continue
        try:
            html = fetch(page).decode('utf-8', 'replace')
            # Accept only the MIDI URL advertised on that particular page.
            match = re.search(r'(?:https?://bitmidi\.com)?(/uploads/\d+\.mid)', html)
            if not match:
                print(f'NOT FOUND: {title} — {page}')
                continue
            midi_url = BASE + match.group(1)
            data = fetch(midi_url)
            if not data.startswith(b'MThd'):
                print(f'INVALID MIDI: {title}')
                continue
            dst.write_bytes(data)
            successes += 1
            print(f'OK {title}: {len(data):,} bytes → {dst}')
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            print(f'FAILED {title}: {exc} — manual download: {page}')
        time.sleep(0.4)
    print(f'\nDownloaded {successes} files to {OUT.resolve()}')
    print('These are community transcriptions, not official production files.')
    print('Keep copyrighted MIDI out of public Git repositories.')

if __name__ == '__main__':
    main()
