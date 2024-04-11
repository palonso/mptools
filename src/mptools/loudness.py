from argparse import ArgumentParser
from essentia.standard import AudioLoader, LoudnessEBUR128
from pathlib import Path


def loudness(audio_path: Path):
    audio, sr, n_channels, _, bit_rate, codec = AudioLoader(filename=str(audio_path))()

    print("loaded audio with:")
    print(f"  sample rate: {sr}")
    print(f"  number of channels: {n_channels}")
    print(f"  bit rate: {bit_rate}")
    print(f"  codec: {codec}")

    _, _, integrated_loudness, loudness_range = LoudnessEBUR128(sampleRate=sr)(audio)

    print(f"Integrated loudness: {integrated_loudness:.3f} LUFS")
    print(f"Loudness range: {loudness_range:.3f} LU")


def main():
    parser = ArgumentParser()
    parser.add_argument("audio", type=Path, help="Path to the audio file")

    args = parser.parse_args()
    audio_file = args.audio
    loudness(audio_file)
