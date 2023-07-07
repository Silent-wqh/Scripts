import sys
import os
from pydub import AudioSegment
import librosa
import numpy as np

def split_audio(start, end, y, sr):
    # 在给定的音频范围内寻找最小强度的位置进行切割
    S, phase = librosa.magphase(librosa.stft(y[int(sr*start/1000):int(sr*end/1000)]))
    rms = librosa.feature.rms(S=S)
    min_rms_index = np.argmin(rms)
    return start + min_rms_index * (1000 / sr)

def main():
    # 定义切割时间间隔，单位为毫秒
    time_interval = 1799 * 1000

    # 从命令行参数获取输入文件路径
    input_file_path = sys.argv[1]
    
    # 加载音频文件
    audio = AudioSegment.from_file(input_file_path)

    # 获取输入文件的目录和文件名
    base_dir, base_name = os.path.split(input_file_path)
    base_name, _ = os.path.splitext(base_name)

    # 开始切割
    start = 0
    end = start + time_interval
    parts = []
    while start < len(audio):
        if end > len(audio):
            end = len(audio)

        # Load only a small chunk of the audio file for RMS calculation
        y, sr = librosa.load(input_file_path, sr=None, offset=start/1000, duration=(end-start)/1000)
        split_point = split_audio(start, end, y, sr)
        parts.append(audio[start:split_point])
        start = split_point
        end = start + time_interval

        # Print progress
        print(f"Progress: {100 * start / len(audio):.2f}%")

    # 保存切割后的音频
    for i, part in enumerate(parts):
        output_file_path = os.path.join(base_dir, f"{base_name}_{i}.wav")
        part.export(output_file_path, format="wav")

if __name__ == "__main__":
    main()
