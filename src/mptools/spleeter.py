from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from essentia.standard import AudioLoader, MonoWriter, TensorflowPredict
from essentia import Pool


SPLEETER_MODEL = "weights/spleeter/spleeter-5s-3.pb"


def spleeter(audio_path: Path):
    audio, sr, n_channels, _, _, _ = AudioLoader(filename=str(audio_path))()

    pool = Pool()

    # The input needs to have 4 dimensions so that it is interpreted as an Essentia tensor.
    pool.set("waveform", audio[..., np.newaxis, np.newaxis])

    stem_names = [
        "waveform_vocals",
        "waveform_drums",
        "waveform_bass",
        "waveform_piano",
        "waveform_other",
    ]

    model = TensorflowPredict(
        graphFilename=SPLEETER_MODEL,
        inputs=["waveform"],
        outputs=stem_names,
    )

    out_pool = model(pool)

    for stem_name in stem_names:
        stem = out_pool[stem_name].squeeze()

        stem_name = stem_name.split("_")[-1]
        output_path = audio_path.with_name(f"{audio_path.stem}_{stem_name}.wav")

        print(f"Writing {output_path}")
        MonoWriter(filename=str(output_path), sampleRate=sr)(stem)

    print("Done!")


def main():
    parser = ArgumentParser()
    parser.add_argument("audio", type=Path, help="Path to the audio file")

    args = parser.parse_args()
    audio_file = args.audio
    spleeter(audio_file)
