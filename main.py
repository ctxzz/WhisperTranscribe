import subprocess
from pydub import AudioSegment
from inaSpeechSegmenter import Segmenter
import os
import csv
import argparse
import glob
import distutils.util

description = """Do Speech/Music(/Noise) and Male/Female segmentation using inaSpeechSegmenter and store segmentations into CSV files.
"""

def wav2seg(args, input_files):
    segmentations = []
    detect_gender = bool(distutils.util.strtobool(args.detect_gender))
    seg = Segmenter(vad_engine=args.vad_engine,
                    detect_gender=detect_gender, ffmpeg=args.ffmpeg_binary)
    for input_file in input_files:
        segmentations += seg(input_file)
    
    print(segmentations)
    return segmentations

def resample_audio(input_path, output_path, target_sample_rate=16000):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(target_sample_rate)
    audio.export(output_path, format="wav")

def transcribe_audio_with_whisper(audio_path):
    temp_resampled_path = "temp_resampled.wav"
    resample_audio(audio_path, temp_resampled_path, target_sample_rate=16000)

    whisper_path = "./whisper.cpp/main"  # Whisperの実行ファイルのパス
    model_path = "whisper.cpp/models/ggml-base.bin"  # 使用するモデルファイルのパス（baseモデル）
    command = [whisper_path, "-f", temp_resampled_path, "--model", model_path, "--language", "ja"]

    # コマンドを実行し、出力を確認する
    result = subprocess.run(command, capture_output=True, text=True)

    # エラーメッセージと出力を表示する
    print("Command:", " ".join(command))
    print("Return Code:", result.returncode)
    print("Error Output:", result.stderr)
    print("Standard Output:", result.stdout)

    return result.stdout.strip()

def parse_transcription(transcription_output):
    transcription = []
    lines = transcription_output.splitlines()

    for line in lines:
        # 行が ']' で始まる場合に、その後の部分を抽出
        if ']' in line:
            # ']' 以降の部分を取得
            content = line.split(']', 1)[1].strip()
            transcription.append(content)
    
    # 発話内容を1つの文字列にまとめる
    return ' '.join(transcription)

def seg2text(segmentations, input_files, output_files):
    for input_file, output_file in zip(input_files, output_files):
        with open(output_file + '.csv', 'w', encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            writer.writerow(['start', 'end', 'label', 'transcript'])

        # 各音声ファイルごとにセグメントをまとめて処理
        for segment in segmentations:
            segment_label = segment[0]
            if (segment_label == 'male' or segment_label == 'female' or segment_label == 'speech'):
                start_time = segment[1] * 1000
                end_time = segment[2] * 1000

                newAudio = AudioSegment.from_file(input_file)
                newAudio = newAudio[start_time:end_time]
                segment_file = output_file + '.wav'  # 各セグメントを1つのファイルにまとめる
                newAudio.export(segment_file, format="wav")

                # Whisperでの音声認識
                transcript_output = transcribe_audio_with_whisper(segment_file)
                transcript = parse_transcription(transcript_output)

                # CSVに書き込む
                with open(output_file + '.csv', 'a', encoding="utf_8_sig") as f:
                    writer = csv.writer(f)
                    writer.writerow([segment[1], segment[2], segment_label, transcript])

                print("Transcript:", transcript)

        with open(output_file + ".csv") as f:
            print(f.read())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--input', nargs='+', help='Input media to analyze. May be a full path to a media file or a regex input pattern.', required=True)
    parser.add_argument('-o', '--output_directory', help='Directory to store segmentations with CSV extension.', required=True)
    parser.add_argument('-d', '--vad_engine', choices=['sm', 'smn'], default='smn',
                        help="Voice activity detection (VAD) engine to be used.")
    parser.add_argument('-g', '--detect_gender', choices=['true', 'false'], default='True',
                        help="If set to 'true', segments detected as speech will be split into 'male' and 'female' segments.")
    parser.add_argument('-b', '--ffmpeg_binary', default='ffmpeg',
                        help='Path to your custom binary of ffmpeg.')
    args = parser.parse_args()

    input_files = []
    for e in args.input:
        if e.startswith("http"):
            input_files += [e]
        else:
            input_files += glob.glob(e)
    assert len(input_files) > 0, 'No existing media selected for analysis! Bad values provided to -i.'

    odir = args.output_directory.strip(" \t\n\r").rstrip('/')
    assert os.access(odir, os.W_OK), 'Directory is not writable!'
    base = [os.path.splitext(os.path.basename(e))[0] for e in input_files]
    output_files = [os.path.join(odir, e) for e in base]

    segmentations = wav2seg(args, input_files)
    seg2text(segmentations, input_files, output_files)