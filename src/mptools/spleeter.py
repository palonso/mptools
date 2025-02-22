from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from essentia.standard import AudioLoader, AudioWriter, Resample, TensorflowPredict
from essentia import Pool


metadata = {
    "2_stems": {
        "stem_names": [
            "waveform_accompaniment",
            "waveform_vocals",
        ],
        "weights": "spleeter-2s-3.pb",
    },
    "4_stems": {
        "stem_names": [
            "waveform_bass",
            "waveform_drums",
            "waveform_other",
            "waveform_vocals",
        ],
        "weights": "spleeter-4s-3.pb",
    },
}

target_sr = 44100
script_dir = Path(__file__).parent


def resample(audio, sr, target_sr):
    """Resample audio to target sample rate."""
    if sr != target_sr:
        print(f"Resampling audio from {sr} to {target_sr}")
        resampler = Resample(inputSampleRate=sr, outputSampleRate=target_sr)
        audio = resampler(audio)
    return audio


def spleeter(audio_path: Path, model: str = "2_stems", format: str = "same"):
    """Use Spleeter to separate the audio into stems."""
    stem_names = metadata[model]["stem_names"]
    weights_file = script_dir / "weights" / "spleeter" / metadata[model]["weights"]

    audio, sr, _, _, _, _ = AudioLoader(filename=str(audio_path))()

    audio = resample(audio, sr, target_sr)

    pool = Pool()

    # The input needs to have 4 dimensions so that it is interpreted as an Essentia tensor.
    pool.set("waveform", audio[..., np.newaxis, np.newaxis])

    model = TensorflowPredict(
        graphFilename=str(weights_file),
        inputs=["waveform"],
        outputs=stem_names,
    )

    out_pool = model(pool)

    for stem_name in stem_names:
        stem = out_pool[stem_name].squeeze()

        stem_name = stem_name.split("_")[-1]
        output_path = audio_path.with_stem(f"{audio_path.stem}.{stem_name}")

        if format != "same":
            output_path = output_path.with_suffix(f".{format}")

        if stem.shape[0] > 0:
            print(f"Writing {output_path}")
            AudioWriter(filename=str(output_path), sampleRate=sr)(stem)
        else:
            print(f"Skipping {stem_name} stem because it is empty")

    print("done!")


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "audio",
        type=Path,
        help="Path to the audio file",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["2_stems", "4_stems"],
        default="4_stems",
        help="Model to use",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="same",
        help="Output audio format. Use `same` to keep the same format",
    )

    args = parser.parse_args()

    spleeter(audio_path=args.audio, model=args.model, format=args.format)
