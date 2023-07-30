import argparse
import shutil
import sys

from pathlib import Path
from typing import Optional
from tracklist.format.cuesheet import CuesheetFormat

from mixport.transcode import transcode

RECORDINGS_PATH = Path.home() / 'Music' / 'Mixxx' / 'Recordings'

def find_latest_recording() -> Optional[Path]:
    '''Fetches the path to the latest recording's .cue file.'''
    return next((path for path in sorted(RECORDINGS_PATH.iterdir(), reverse=True) if path.name.endswith('.cue')), None)

def main():
    parser = argparse.ArgumentParser(description='CLI tool for transcoding Mixxx recordings')
    parser.add_argument('-o', '--output', required=True, type=Path, help='The output directory.')
    parser.add_argument('-f', '--format', default='opus', help='The file extension of the output format. Has to be a format that ffmpeg supports.')
    parser.add_argument('input', type=Path, nargs=argparse.OPTIONAL, help='The input cue file. Defaults to the latest Mixxx recording.')

    args = parser.parse_args()

    in_cue_path = args.input or find_latest_recording()
    out_dir = args.output
    format = args.format

    if not in_cue_path:
        print(f'No recording (.cue file) found in recordings: {RECORDINGS_PATH}')
        sys.exit(1)

    print(f'==> Parsing {in_cue_path}')
    with open(in_cue_path, 'r') as f:
        tracklist = CuesheetFormat().parse(f.read())

    if not tracklist.file:
        print(f'No audio file referenced in {in_cue_path}!')
        sys.exit(1)
    
    in_audio_path = RECORDINGS_PATH / tracklist.file

    print(f'==> Checking {in_audio_path}')
    if not in_audio_path.exists():
        print(f'Non-existent audio file {in_audio_path} referenced in {in_cue_path}!')
        sys.exit(1)

    out_cue_path = out_dir / in_cue_path.name
    out_audio_path = out_dir / in_cue_path.with_suffix(f'.{format}').name

    print(f'==> Creating {out_dir} if needed')
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f'==> Copying to {out_cue_path}')
    shutil.copy(in_cue_path, out_cue_path)

    print(f'==> Transcoding to {out_audio_path}')
    transcode(
        in_audio_path=in_audio_path,
        out_audio_path=out_audio_path
    )
