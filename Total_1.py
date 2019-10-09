'''
去掉静音区
'''

import wave
import os
import numpy as np
import matplotlib.pyplot as plt
import contextlib
import io
plt.switch_backend('agg')
#定义一个符函数
def sgn(data):
    if data >= 0:
        return 1
    else:
        return 0

# 计算每一帧的能量 256个采样点为一帧
def calEnergy(wave_data):
    energy = []
    sum = 0
    for i in range(len(wave_data)):
        sum = sum + (int(wave_data[i]) * int(wave_data[i]))    # 计算每一帧的短时能量
        if (i + 1) % 256 == 0:
            energy.append(sum)
            sum = 0
        elif i == len(wave_data) - 1:
            energy.append(sum)
    return energy
#计算过零率
def calZeroCrossingRate(wave_data):
    zeroCrossingRate = []
    sum = 0
    for i in range(len(wave_data)):
        if i % 256 == 0:
            continue
        sum = sum + np.abs(sgn(wave_data[i]) - sgn(wave_data[i - 1]))
        if (i + 1) % 256 == 0:
            zeroCrossingRate.append(float(sum) / 255)
            sum = 0
        elif i == len(wave_data) - 1:
            zeroCrossingRate.append(float(sum) / 255)
    return zeroCrossingRate

# 利用短时能量，短时过零率，使用双门限法进行端点检测
def endPointDetect(wave_data, energy, zeroCrossingRate):
    sum = 0
    energyAverage = 0
    for en in energy:
        sum = sum + en
    energyAverage = sum / len(energy)  #平均能量

    sum = 0
    # 语音前一段的静音部分的能量均值（前5帧）
    for en in energy[:5]:
        sum = sum + en
    ML = sum / 5
    MH = energyAverage / 4              # 较高的能量阈值
    ML = (ML + MH) / 4                  # 较低的能量阈值
    sum = 0
    for zcr in zeroCrossingRate[:5]:
        sum = float(sum) + zcr
    Zs = sum / 5                     # 过零率阈值

    A = []

    # 利用较大能量阈值 MH 进行初步检测
    flag = 0
    for i in range(len(energy)):
        if len(A) == 0 and flag == 0 and energy[i] > MH:     # 先找出第一个较大能量阀值点A1
            A.append(i)
            flag = 1
        elif flag == 0 and energy[i] > MH and i - 21 > A[len(A) - 1]:
            A.append(i)
            flag = 1
        elif flag == 0 and energy[i] > MH and i - 21 <= A[len(A) - 1]:
            A = A[:len(A) - 1]
            flag = 1

        if flag == 1 and energy[i] < MH:       # 找到第二个较大能量阈值点A2
            A.append(i)
            flag = 0
    #print("较高能量阈值，计算后的浊音A:" + str(A))
    return A

# 去掉音频静音区
def cut_silence(wavfile, path_out):
    # files = os.listdir(path)                # 遍历文件夹中的文件
    # files = [path + f for f in files if f.endswith('.wav')]     # 选取wav格式的文件
    # for i in range(len(files)):
    # filesName = files[i]
    file = wave.open(io.BytesIO(wavfile), "rb")
    params = file.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = file.readframes(nframes)
    wave_data = np.fromstring(str_data, dtype=np.short)
    energy = calEnergy(wave_data)
    zeroCrossingRate = calZeroCrossingRate(wave_data)
    N = endPointDetect(wave_data, energy, zeroCrossingRate)
    with open(path_out + "wavfile.pcm", "wb") as f:
        i = 0
        while i < len(N)-1:
            for num in wave_data[N[i] * 256: N[i + 1] * 256]:
                f.write(num)
            i = i + 2
# pcm格式文档转wav
def pcm_to_wav(pcm_path, wav_path):
    # filename = os.listdir(pcm_path)
    # for name in filename:
    with open(pcm_path + "wavfile.pcm", 'rb') as f:
        # print(f)
        str_data = f.read()
        path = wav_path + "wavfile" + '.wav'
        wave_out = wave.open(path, 'wb')
        wave_out.setnchannels(2)
        wave_out.setsampwidth(2)
        wave_out.setframerate(44100)
        wave_out.writeframes(str_data)
    #print("完成pcm转wav")

def get_wav_time(file):
    '''
    获取音频文件时长
    :param wav_path: 音频路径
    :return: 音频时长 (单位秒)
    '''
    # files = os.listdir(wav_path)
    # for i in range(len(files)):
    #     file = files[i]
    # with contextlib.closing(wave.open(wav_path + "/" + file, 'r')) as f:
    with contextlib.closing(wave.open(file, 'r')) as f:
        frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    #print(duration)
    return duration

# 将音频剪切成2s
def cutfile(wav_path, cut_path, cut_time):
    files = os.listdir(wav_path)  # 遍历文件夹中的文件
    files = [wav_path + f for f in files if f.endswith('.wav')]  # 选取wav格式的文件
    for i in range(len(files)):                     # 遍历文件中的数量
        FileName = files[i]
        f = wave.open(r"" + FileName, "rb")
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        CutFrameNum = framerate * cut_time              # 频率乘时间
        str_data = f.readframes(nframes)
        f.close()  # 将波形数据转换成数组
        wave_data = np.fromstring(str_data, dtype=np.short)
        if nchannels == 2:
            wave_data.shape = -1, 2
        wave_data = wave_data.T
        temp_data = wave_data.T
        StepNum = CutFrameNum
        StepTotalNum = 0
        haha = 0
        while StepTotalNum < nframes:
            FileName = cut_path +  "wavfile_" + str(haha + 1) + ".wav"
            temp_dataTemp = temp_data[StepNum * (haha):StepNum * (haha + 1)]
            haha = haha + 1
            StepTotalNum = haha * StepNum
            temp_dataTemp.shape = 1, -1
            temp_dataTemp = temp_dataTemp.astype(np.short)  # 打开WAV文档
            f = wave.open(FileName, "wb")
            f.setnchannels(nchannels)
            f.setsampwidth(sampwidth)
            f.setframerate(framerate)
            f.writeframes(temp_dataTemp.tostring())
            f.close()
    #print("完成切割")

def draw_spectrogram(cut_path, draw_path):
    files = os.listdir(cut_path)
    for i in range(len(files)):
        file = files[i]
        f = wave.open(cut_path+file, 'rb')
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        strData = f.readframes(nframes)
        waveData = np.fromstring(strData, dtype=np.int16)
        waveData = waveData * 1.0 / max(abs(waveData))
        waveData = np.reshape(waveData, [nframes, nchannels]).T
        f.close()
        # 绘制频谱
        framelength = 0.025
        framesize = framelength * framerate     # 512
        nfftdict = {}
        lists = [32, 64, 128, 256, 512, 1024, 2048]
        for i in lists:
            nfftdict[i] = abs(framesize - i)
        sortlist = sorted(nfftdict.items(), key=lambda x: x[1])  # 按与当前framesize差值升序排列
        framesize = int(sortlist[0][0])
        NFFT = framesize
        overlapSize = 1.0 / 3 * framesize
        overlapSize = int(round(overlapSize))
        spectrum, freqs, ts, fig =plt.specgram(waveData[0], NFFT=2048, Fs=2, Fc=0,
             window=np.hamming(M=2048), noverlap=1536,
             cmap='jet', xextent=None, pad_to=None, sides='default',
             scale_by_freq=None, mode='default', scale='default')
        plt.axis('off')
        fig = plt.gcf()
        fig.set_size_inches(2.56 / 5, 2.56 / 5)  # dpi = 300, output = 700*700 pixels
        out_jpg_path = draw_path + os.path.splitext(file)[0] + '.jpg'
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        fig.savefig(out_jpg_path, format='jpg', transparent=True, dpi=500, pad_inches=0)        # dpi是dots per inch, 就是说一英寸上有多少个点
        # plt.show()
        plt.close()
        #print(" ")

# if __name__ == "__main__":
#     path = "E:/contest/data/voice1"  # 文件路径名
#     path_out = "E:/contest/data/voice2"
#     pcm_path = path_out
#     wav_path = "E:/contest/data/voice3"
#     cut_path = "E:/contest/data/voice4"
#     cut_silence(path, path_out)
#     pcm_to_wav(pcm_path, wav_path)
#     cutfile(wav_path, cut_path, 2)
#     draw_path = "E:/contest/data/picture/"
#     draw_spectrogram(cut_path, draw_path)
# path = "E:/contest/data/voice1/"  # 文件路径名
# draw_path = "E:/contest/data/picture/"
def generator_image(path, draw_path):
    path_out = "data/voice2/"
    pcm_path = path_out
    wav_path = "data/voice3/"
    cut_silence(path, path_out)         # 去除静音区（端点检测），生成pcm格式文件
    pcm_to_wav(pcm_path, wav_path)
    #print("================"+wav_path)
    # 将pcm转换成wav
    #files = os.listdir(wav_path)
    #for i in range(len(files)):
    file = wav_path+"wavfile.wav"
    duration = get_wav_time(file)
    if duration < 2:
        #print("有效时长不足，请重新输入")
        for i in os.listdir(wav_path):
            path_file = os.path.join(wav_path, i)
            #print("删除文件了")
            os.remove(path_file)
            # os.remove(wav_path + path_file)
    else:
        cut_path = "data/voice4/"
        cutfile(wav_path, cut_path, 2)  # 去掉静音区的音频大于2s，进行音频切割
        files = os.listdir(cut_path)
        for i in range(len(files)):
            file = files[i]
            second = get_wav_time(cut_path + file)
            if second < 2:
                os.remove(cut_path + file)
                #print("删除文件" + file)
        for i in os.listdir("data/picture"):
            remove_path_file = os.path.join("data/picture", i)
            os.remove(remove_path_file)
        draw_spectrogram(cut_path, draw_path)
        for i in os.listdir("data/voice2"):
            remove_path_file = os.path.join("data/voice2", i)
            #print("删除文件了")
            os.remove(remove_path_file)
        for i in os.listdir("data/voice3"):
            remove_path_file = os.path.join("data/voice3", i)
            # print("删除文件了")
            os.remove(remove_path_file)
        for i in os.listdir("data/voice4"):
            remove_path_file = os.path.join("data/voice4", i)
            # print("删除文件了")
            os.remove(remove_path_file)
        picture_list = os.listdir(draw_path)
        return picture_list
# path = "E:/contest/data/voice1/"  # 文件路径名
# draw_path = "E:/contest/data/picture/"
# main(path, draw_path)


