from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from essentia.standard import AudioLoader, AudioWriter
from essentia import db2amp


def normalize(audio_path: Path, headroom: float, format: str = "same"):
    """Normalize an audio file leaving a given headroom"""

    audio_path = Path(audio_path)
    audio, sr, _, _, bit_rate, _ = AudioLoader(filename=str(audio_path))()

    tgt = db2amp(headroom)
    peak = np.max(np.abs(audio))

    audio_n = audio * tgt / peak

    output_path = audio_path.with_stem(f"{audio_path.stem}.normalized")

    if format != "same":
        output_path = output_path.with_suffix(f".{format}")

    # TODO: Use input bit rate. Skipping for now since for some formats
    # the bit_rate value is not appropriate. e.g., aif reported 2116800
    AudioWriter(filename=str(output_path), sampleRate=sr)(audio_n)

    print("done!")


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "audio",
        type=Path,
        help="Path to the audio file",
    )
    parser.add_argument(
        "--headroom",
        type=float,
        default=-0.2,
        help="Headroom in dB",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="same",
        help="Output audio format. Use `same` to keep the same format",
    )

    args = parser.parse_args()
    normalize(
        audio_path=args.audio,
        headroom=args.headroom,
        format=args.format,
    )
