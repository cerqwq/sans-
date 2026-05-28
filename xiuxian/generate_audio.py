"""
生成游戏音频文件（WAV格式）并编码为base64
高级版本：更长的BGM、更丰富的音效、环境音
"""
import struct
import math
import base64
import wave
import io
import random

def generate_sine_wave(freq, duration, sample_rate=44100, amplitude=0.3):
    """生成正弦波"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * freq * t)
        fade_len = int(sample_rate * 0.01)
        if i < fade_len:
            sample *= i / fade_len
        elif i > total - fade_len:
            sample *= (total - i) / fade_len
        samples.append(sample)
    return samples

def generate_tone(freq, duration, sample_rate=44100, amplitude=0.3, wave_type='sine'):
    """生成不同波形"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        phase = 2 * math.pi * freq * t
        if wave_type == 'sine':
            sample = amplitude * math.sin(phase)
        elif wave_type == 'triangle':
            sample = amplitude * (2 * abs(2 * (freq * t % 1) - 1) - 1)
        elif wave_type == 'sawtooth':
            sample = amplitude * (2 * (freq * t % 1) - 1)
        elif wave_type == 'square':
            sample = amplitude * (1 if math.sin(phase) > 0 else -1)
        else:
            sample = amplitude * math.sin(phase)
        fade_len = int(sample_rate * 0.005)
        if i < fade_len:
            sample *= i / fade_len
        elif i > total - fade_len:
            sample *= (total - i) / fade_len
        samples.append(sample)
    return samples

def generate_chord(freqs, duration, sample_rate=44100, amplitude=0.2):
    """生成和弦"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        sample = 0
        for freq in freqs:
            sample += amplitude * math.sin(2 * math.pi * freq * t)
        fade_len = int(sample_rate * 0.02)
        if i < fade_len:
            sample *= i / fade_len
        elif i > total - fade_len:
            sample *= (total - i) / fade_len
        samples.append(sample / len(freqs))
    return samples

def generate_noise(duration, sample_rate=44100, amplitude=0.1):
    """生成白噪声"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        sample = amplitude * (random.random() * 2 - 1)
        fade_len = int(sample_rate * 0.005)
        if i < fade_len:
            sample *= i / fade_len
        elif i > total - fade_len:
            sample *= (total - i) / fade_len
        samples.append(sample)
    return samples

def generate_filtered_noise(duration, sample_rate=44100, amplitude=0.1, cutoff=1000):
    """生成低通滤波噪声"""
    samples = []
    total = int(sample_rate * duration)
    prev = 0
    alpha = min(1.0, cutoff / (sample_rate * 0.5))
    for i in range(total):
        noise = amplitude * (random.random() * 2 - 1)
        filtered = alpha * noise + (1 - alpha) * prev
        prev = filtered
        fade_len = int(sample_rate * 0.005)
        if i < fade_len:
            filtered *= i / fade_len
        elif i > total - fade_len:
            filtered *= (total - i) / fade_len
        samples.append(filtered)
    return samples

def generate_drum_hit(duration=0.15, sample_rate=44100, amplitude=0.4):
    """生成鼓声（低频冲击）"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        freq = 150 * math.exp(-t * 30)  # 频率快速衰减
        sample = amplitude * math.sin(2 * math.pi * freq * t) * math.exp(-t * 8)
        sample += amplitude * 0.3 * (random.random() * 2 - 1) * math.exp(-t * 15)
        samples.append(sample)
    return samples

def generate_hihat(duration=0.05, sample_rate=44100, amplitude=0.2):
    """生成踩镲声"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        sample = amplitude * (random.random() * 2 - 1) * math.exp(-t * 40)
        # 高通效果
        if i > 0:
            sample = sample - 0.95 * (amplitude * (random.random() * 2 - 1) * math.exp(-t * 40))
        samples.append(sample)
    return samples

def generate_bell(freq, duration=1.0, sample_rate=44100, amplitude=0.2):
    """生成钟声/铃声"""
    samples = []
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * freq * t) * math.exp(-t * 2)
        sample += amplitude * 0.5 * math.sin(2 * math.pi * freq * 2.76 * t) * math.exp(-t * 3)
        sample += amplitude * 0.3 * math.sin(2 * math.pi * freq * 5.4 * t) * math.exp(-t * 5)
        samples.append(sample)
    return samples

def generate_wind(duration, sample_rate=44100, amplitude=0.08):
    """生成风声"""
    samples = []
    total = int(sample_rate * duration)
    prev = 0
    for i in range(total):
        t = i / sample_rate
        noise = random.random() * 2 - 1
        # 低通滤波
        filtered = 0.02 * noise + 0.98 * prev
        prev = filtered
        # 调制振幅
        mod = 0.5 + 0.5 * math.sin(2 * math.pi * 0.3 * t)
        sample = amplitude * filtered * mod * 3
        samples.append(sample)
    return samples

def generate_water_drop(sample_rate=44100, amplitude=0.15):
    """生成水滴声"""
    samples = []
    freq = 800 + random.random() * 400
    duration = 0.3
    total = int(sample_rate * duration)
    for i in range(total):
        t = i / sample_rate
        freq_mod = freq * math.exp(-t * 5)
        sample = amplitude * math.sin(2 * math.pi * freq_mod * t) * math.exp(-t * 8)
        samples.append(sample)
    return samples

def generate_flute_melody(notes, duration_per_note=0.4, sample_rate=44100, amplitude=0.2):
    """生成笛子旋律"""
    samples = []
    for freq in notes:
        total = int(sample_rate * duration_per_note)
        for i in range(total):
            t = i / sample_rate
            # 带泛音的笛子音色
            sample = amplitude * math.sin(2 * math.pi * freq * t)
            sample += amplitude * 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            sample += amplitude * 0.1 * math.sin(2 * math.pi * freq * 3 * t)
            # 颤音
            vibrato = 1 + 0.02 * math.sin(2 * math.pi * 5 * t)
            sample *= vibrato
            # 包络
            attack = min(1, t / 0.05)
            decay = math.exp(-t * 2) if t > 0.05 else 1
            envelope = attack * decay
            # 淡入淡出
            fade_len = int(sample_rate * 0.01)
            if i < fade_len:
                envelope *= i / fade_len
            elif i > total - fade_len:
                envelope *= (total - i) / fade_len
            samples.append(sample * envelope)
    return samples

def generate_guzheng_melody(notes, duration_per_note=0.3, sample_rate=44100, amplitude=0.2):
    """生成古筝旋律"""
    samples = []
    for freq in notes:
        total = int(sample_rate * duration_per_note)
        for i in range(total):
            t = i / sample_rate
            # 古筝：拨弦音色，快速衰减
            sample = amplitude * math.sin(2 * math.pi * freq * t) * math.exp(-t * 4)
            sample += amplitude * 0.4 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-t * 6)
            sample += amplitude * 0.2 * math.sin(2 * math.pi * freq * 3 * t) * math.exp(-t * 10)
            # 淡入淡出
            fade_len = int(sample_rate * 0.005)
            if i < fade_len:
                sample *= i / fade_len
            elif i > total - fade_len:
                sample *= (total - i) / fade_len
            samples.append(sample)
    return samples

def samples_to_wav_base64(samples, sample_rate=44100):
    """将采样数据转换为WAV格式的base64字符串"""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for s in samples:
            s = max(-1, min(1, s))
            wf.writeframes(struct.pack('<h', int(s * 32767)))
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')

def mix_samples(*sample_lists, volumes=None):
    """混合多条音轨"""
    max_len = max(len(s) for s in sample_lists)
    if volumes is None:
        volumes = [1.0] * len(sample_lists)
    mixed = []
    for i in range(max_len):
        val = 0
        for j, samples in enumerate(sample_lists):
            if i < len(samples):
                val += samples[i] * volumes[j]
        mixed.append(val)
    return mixed

def generate_all_audio():
    """生成所有游戏音频"""
    audio = {}

    # ================================================================
    # BGM 音乐（更长、更丰富的编曲）
    # ================================================================

    # 1. 青云镇 — 平和古风（6秒）
    bgm_peaceful = []
    guzheng_melody = [262, 294, 330, 392, 440, 523, 440, 392]
    guzheng = generate_guzheng_melody(guzheng_melody, 0.4, amplitude=0.15)
    flute_melody = [523, 587, 659, 784, 880, 1047, 880, 784]
    flute = generate_flute_melody(flute_melody, 0.4, amplitude=0.1)
    drums = []
    for _ in range(8):
        drums.extend(generate_drum_hit(0.15, amplitude=0.08))
        drums.extend(generate_hihat(0.05, amplitude=0.04))
        drums.extend([0] * int(44100 * 0.2))
    chords_peaceful = []
    for _ in range(2):
        chords_peaceful.extend(generate_chord([262, 330, 392], 0.8, amplitude=0.08))
        chords_peaceful.extend(generate_chord([294, 370, 440], 0.8, amplitude=0.08))
        chords_peaceful.extend(generate_chord([330, 415, 494], 0.8, amplitude=0.08))
        chords_peaceful.extend(generate_chord([262, 330, 392], 0.8, amplitude=0.08))
    bgm_peaceful = mix_samples(guzheng, flute, drums, chords_peaceful, volumes=[1, 0.8, 0.6, 0.5])
    audio["bgm_peaceful"] = samples_to_wav_base64(bgm_peaceful)

    # 2. 战斗 — 激烈紧张（6秒）
    bgm_battle = []
    battle_drums = []
    for _ in range(12):
        battle_drums.extend(generate_drum_hit(0.08, amplitude=0.25))
        battle_drums.extend(generate_hihat(0.03, amplitude=0.1))
        battle_drums.extend(generate_drum_hit(0.08, amplitude=0.15))
        battle_drums.extend(generate_hihat(0.03, amplitude=0.08))
    bass = []
    for freq in [110, 110, 130.8, 130.8, 146.8, 146.8, 130.8, 130.8] * 2:
        bass.extend(generate_tone(freq, 0.2, amplitude=0.2, wave_type='sawtooth'))
    battle_melody = []
    for freq in [330, 349, 392, 440, 392, 349, 330, 294] * 2:
        battle_melody.extend(generate_tone(freq, 0.15, amplitude=0.12, wave_type='square'))
        battle_melody.extend([0] * int(44100 * 0.05))
    tension = []
    for _ in range(6):
        tension.extend(generate_chord([220, 277, 330], 0.4, amplitude=0.06))
        tension.extend(generate_chord([233, 293, 349], 0.4, amplitude=0.06))

    bgm_battle = mix_samples(battle_drums, bass, battle_melody, tension, volumes=[1, 0.8, 0.6, 0.4])
    audio["bgm_battle"] = samples_to_wav_base64(bgm_battle)

    # 3. 幽冥 — 阴森诡异（6秒）
    bgm_dark = []
    dark_pulse = []
    for _ in range(6):
        dark_pulse.extend(generate_sine_wave(55, 0.5, amplitude=0.15))
        dark_pulse.extend(generate_sine_wave(52, 0.5, amplitude=0.12))
    wind = generate_wind(6, amplitude=0.06)
    dissonance = []
    for _ in range(3):
        dissonance.extend(generate_chord([110, 117, 130], 1.0, amplitude=0.05))
        dissonance.extend(generate_chord([103, 110, 117], 1.0, amplitude=0.05))
    drips = []
    for _ in range(3):
        drips.extend([0] * int(44100 * (1 + random.random())))
        drips.extend(generate_water_drop(amplitude=0.08))

    bgm_dark = mix_samples(dark_pulse, wind, dissonance, drips, volumes=[1, 0.7, 0.6, 0.5])
    audio["bgm_dark"] = samples_to_wav_base64(bgm_dark)

    # 4. 天玄 — 庄严神圣（6秒）
    bgm_majestic = []
    bells = []
    for freq in [196, 220, 247, 262, 294, 330]:
        bells.extend(generate_bell(freq, 0.8, amplitude=0.1))
        bells.extend([0] * int(44100 * 0.2))
    maj_chords = []
    for _ in range(2):
        maj_chords.extend(generate_chord([196, 247, 294], 0.8, amplitude=0.1))
        maj_chords.extend(generate_chord([220, 277, 330], 0.8, amplitude=0.1))
        maj_chords.extend(generate_chord([247, 311, 370], 0.8, amplitude=0.1))
        maj_chords.extend(generate_chord([262, 330, 392], 0.8, amplitude=0.1))
    pad = []
    for _ in range(6):
        pad.extend(generate_sine_wave(784, 0.5, amplitude=0.04))
        pad.extend(generate_sine_wave(880, 0.5, amplitude=0.04))

    bgm_majestic = mix_samples(bells, maj_chords, pad, volumes=[0.8, 1, 0.5])
    audio["bgm_majestic"] = samples_to_wav_base64(bgm_majestic)

    # 5. 混沌 — 空灵飘渺（6秒）
    bgm_ethereal = []
    ethereal = []
    for _ in range(6):
        ethereal.extend(generate_sine_wave(880, 0.3, amplitude=0.06))
        ethereal.extend(generate_sine_wave(1047, 0.3, amplitude=0.05))
        ethereal.extend(generate_sine_wave(1319, 0.3, amplitude=0.04))
        ethereal.extend(generate_sine_wave(1047, 0.3, amplitude=0.05))
    eth_wind = generate_wind(6, amplitude=0.04)
    eth_chords = []
    for _ in range(2):
        eth_chords.extend(generate_chord([440, 554, 659], 1.5, amplitude=0.04))
        eth_chords.extend(generate_chord([523, 659, 784], 1.5, amplitude=0.04))
        eth_chords.extend(generate_chord([440, 554, 659], 1.5, amplitude=0.04))

    bgm_ethereal = mix_samples(ethereal, eth_wind, eth_chords, volumes=[1, 0.5, 0.6])
    audio["bgm_ethereal"] = samples_to_wav_base64(bgm_ethereal)

    # 6. 秘境 — 神秘探索（6秒）
    bgm_dungeon = []
    dungeon_base = []
    for _ in range(12):
        dungeon_base.extend(generate_sine_wave(98, 0.25, amplitude=0.1))
        dungeon_base.extend(generate_sine_wave(110, 0.25, amplitude=0.08))
    dungeon_melody = []
    for freq in [262, 294, 311, 330, 349, 330, 311, 294] * 2:
        dungeon_melody.extend(generate_flute_melody([freq], 0.4, amplitude=0.1))
    dungeon_ambient = []
    for _ in range(4):
        dungeon_ambient.extend(generate_water_drop(amplitude=0.05))
        dungeon_ambient.extend([0] * int(44100 * (0.5 + random.random())))
    bgm_dungeon = mix_samples(dungeon_base, dungeon_melody, dungeon_ambient, volumes=[0.8, 1, 0.4])
    audio["bgm_dungeon"] = samples_to_wav_base64(bgm_dungeon)

    # 7. 宗门 — 古朴大气（6秒）
    bgm_sect = []
    sect_guzheng = generate_guzheng_melody([392, 440, 523, 587, 659, 523, 440, 392], 0.5, amplitude=0.15)
    sect_chords = []
    for _ in range(2):
        sect_chords.extend(generate_chord([196, 262, 330], 1.0, amplitude=0.08))
        sect_chords.extend(generate_chord([220, 294, 349], 1.0, amplitude=0.08))
        sect_chords.extend(generate_chord([262, 330, 392], 1.0, amplitude=0.08))
        sect_chords.extend(generate_chord([220, 294, 349], 1.0, amplitude=0.08))
    sect_bells = []
    for freq in [523, 659]:
        sect_bells.extend(generate_bell(freq, 0.8, amplitude=0.05))
        sect_bells.extend([0] * int(44100 * 0.5))
    bgm_sect = mix_samples(sect_guzheng, sect_chords, sect_bells, volumes=[1, 0.6, 0.4])
    audio["bgm_sect"] = samples_to_wav_base64(bgm_sect)

    # 8. BOSS战 — 史诗激烈（6秒）
    bgm_boss = []
    boss_drums = []
    for _ in range(16):
        boss_drums.extend(generate_drum_hit(0.1, amplitude=0.3))
        boss_drums.extend(generate_hihat(0.04, amplitude=0.12))
        boss_drums.extend(generate_drum_hit(0.1, amplitude=0.2))
        boss_drums.extend(generate_hihat(0.04, amplitude=0.1))
    boss_bass = []
    for freq in [82.4, 82.4, 98, 98, 110, 110, 98, 98] * 2:
        boss_bass.extend(generate_tone(freq, 0.2, amplitude=0.25, wave_type='sawtooth'))
    boss_melody = []
    for freq in [330, 392, 440, 523, 440, 392, 330, 294, 330, 392, 440, 523, 587, 523, 440, 392]:
        boss_melody.extend(generate_tone(freq, 0.15, amplitude=0.15, wave_type='square'))
        boss_melody.extend([0] * int(44100 * 0.05))
    boss_chords = []
    for _ in range(4):
        boss_chords.extend(generate_chord([165, 208, 247], 0.5, amplitude=0.08))
        boss_chords.extend(generate_chord([175, 220, 262], 0.5, amplitude=0.08))
    bgm_boss = mix_samples(boss_drums, boss_bass, boss_melody, boss_chords, volumes=[1, 0.8, 0.6, 0.4])
    audio["bgm_boss"] = samples_to_wav_base64(bgm_boss)

    # ================================================================
    # 音效（更多种类、更精细）
    # ================================================================

    # 攻击音效
    sfx = generate_noise(0.08, amplitude=0.5)
    sfx.extend(generate_sine_wave(200, 0.1, amplitude=0.3))
    sfx.extend(generate_noise(0.03, amplitude=0.3))
    audio["sfx_attack"] = samples_to_wav_base64(sfx)

    # 受击音效
    sfx = generate_noise(0.05, amplitude=0.6)
    sfx.extend(generate_sine_wave(150, 0.15, amplitude=0.4))
    sfx.extend(generate_drum_hit(0.1, amplitude=0.2))
    audio["sfx_hit"] = samples_to_wav_base64(sfx)

    # 技能音效
    sfx = generate_sine_wave(400, 0.08, amplitude=0.3)
    sfx.extend(generate_sine_wave(600, 0.08, amplitude=0.3))
    sfx.extend(generate_sine_wave(800, 0.08, amplitude=0.3))
    sfx.extend(generate_sine_wave(1000, 0.12, amplitude=0.2))
    audio["sfx_skill"] = samples_to_wav_base64(sfx)

    # 暴击音效
    sfx = generate_noise(0.05, amplitude=0.7)
    sfx.extend(generate_drum_hit(0.08, amplitude=0.4))
    sfx.extend(generate_sine_wave(300, 0.05, amplitude=0.5))
    sfx.extend(generate_sine_wave(500, 0.05, amplitude=0.5))
    sfx.extend(generate_sine_wave(700, 0.1, amplitude=0.4))
    audio["sfx_crit"] = samples_to_wav_base64(sfx)

    # 胜利音效
    sfx = generate_chord([262, 330, 392], 0.3)
    sfx.extend(generate_chord([330, 415, 494], 0.3))
    sfx.extend(generate_chord([392, 494, 587], 0.6))
    sfx.extend(generate_bell(784, 0.5, amplitude=0.1))
    audio["sfx_victory"] = samples_to_wav_base64(sfx)

    # 失败音效
    sfx = generate_sine_wave(200, 0.3, amplitude=0.3)
    sfx.extend(generate_sine_wave(150, 0.3, amplitude=0.3))
    sfx.extend(generate_sine_wave(100, 0.5, amplitude=0.3))
    audio["sfx_defeat"] = samples_to_wav_base64(sfx)

    # 突破成功
    sfx = generate_sine_wave(523, 0.2, amplitude=0.3)
    sfx.extend(generate_sine_wave(659, 0.2, amplitude=0.3))
    sfx.extend(generate_sine_wave(784, 0.2, amplitude=0.3))
    sfx.extend(generate_sine_wave(1047, 0.4, amplitude=0.4))
    sfx.extend(generate_bell(1047, 0.8, amplitude=0.15))
    audio["sfx_breakthrough"] = samples_to_wav_base64(sfx)

    # 按钮点击
    sfx = generate_sine_wave(800, 0.05, amplitude=0.2)
    sfx.extend(generate_sine_wave(1000, 0.03, amplitude=0.1))
    audio["sfx_click"] = samples_to_wav_base64(sfx)

    # 获得物品
    sfx = generate_sine_wave(600, 0.1, amplitude=0.2)
    sfx.extend(generate_sine_wave(800, 0.1, amplitude=0.2))
    sfx.extend(generate_bell(1200, 0.3, amplitude=0.1))
    audio["sfx_item"] = samples_to_wav_base64(sfx)

    # 打开面板
    sfx = generate_sine_wave(400, 0.05, amplitude=0.2)
    sfx.extend(generate_sine_wave(600, 0.05, amplitude=0.2))
    audio["sfx_open"] = samples_to_wav_base64(sfx)

    # 关闭面板
    sfx = generate_sine_wave(600, 0.05, amplitude=0.2)
    sfx.extend(generate_sine_wave(400, 0.05, amplitude=0.2))
    audio["sfx_close"] = samples_to_wav_base64(sfx)

    # 治疗音效
    sfx = generate_sine_wave(523, 0.15, amplitude=0.2)
    sfx.extend(generate_sine_wave(659, 0.15, amplitude=0.2))
    sfx.extend(generate_sine_wave(784, 0.15, amplitude=0.2))
    sfx.extend(generate_bell(1047, 0.4, amplitude=0.1))
    audio["sfx_heal"] = samples_to_wav_base64(sfx)

    # 强化成功
    sfx = generate_drum_hit(0.1, amplitude=0.3)
    sfx.extend(generate_sine_wave(440, 0.1, amplitude=0.3))
    sfx.extend(generate_sine_wave(554, 0.1, amplitude=0.3))
    sfx.extend(generate_sine_wave(659, 0.1, amplitude=0.3))
    sfx.extend(generate_sine_wave(880, 0.2, amplitude=0.4))
    sfx.extend(generate_bell(880, 0.5, amplitude=0.1))
    audio["sfx_enhance"] = samples_to_wav_base64(sfx)

    # 强化失败
    sfx = generate_noise(0.1, amplitude=0.4)
    sfx.extend(generate_sine_wave(200, 0.2, amplitude=0.3))
    sfx.extend(generate_sine_wave(150, 0.15, amplitude=0.2))
    audio["sfx_enhance_fail"] = samples_to_wav_base64(sfx)

    # 灵宠捕获
    sfx = generate_sine_wave(523, 0.1, amplitude=0.2)
    sfx.extend(generate_sine_wave(659, 0.1, amplitude=0.2))
    sfx.extend(generate_sine_wave(784, 0.1, amplitude=0.2))
    sfx.extend(generate_sine_wave(1047, 0.1, amplitude=0.2))
    sfx.extend(generate_sine_wave(1319, 0.2, amplitude=0.3))
    sfx.extend(generate_bell(1319, 0.6, amplitude=0.1))
    audio["sfx_pet_catch"] = samples_to_wav_base64(sfx)

    # 秘境进入
    sfx = generate_sine_wave(200, 0.2, amplitude=0.2)
    sfx.extend(generate_sine_wave(300, 0.2, amplitude=0.2))
    sfx.extend(generate_sine_wave(400, 0.2, amplitude=0.2))
    sfx.extend(generate_sine_wave(500, 0.3, amplitude=0.3))
    sfx.extend(generate_filtered_noise(0.3, amplitude=0.15, cutoff=500))
    audio["sfx_dungeon_enter"] = samples_to_wav_base64(sfx)

    # 升级音效
    sfx = generate_sine_wave(440, 0.15, amplitude=0.2)
    sfx.extend(generate_sine_wave(554, 0.15, amplitude=0.2))
    sfx.extend(generate_sine_wave(659, 0.15, amplitude=0.2))
    sfx.extend(generate_sine_wave(880, 0.15, amplitude=0.25))
    sfx.extend(generate_sine_wave(1047, 0.3, amplitude=0.3))
    audio["sfx_levelup"] = samples_to_wav_base64(sfx)

    # 金币/灵石音效
    sfx = generate_bell(1200, 0.15, amplitude=0.15)
    sfx.extend(generate_bell(1500, 0.15, amplitude=0.12))
    audio["sfx_coin"] = samples_to_wav_base64(sfx)

    # 警告音效
    sfx = generate_sine_wave(300, 0.15, amplitude=0.3)
    sfx.extend([0] * int(44100 * 0.1))
    sfx.extend(generate_sine_wave(300, 0.15, amplitude=0.3))
    audio["sfx_warning"] = samples_to_wav_base64(sfx)

    # 连击音效
    sfx = generate_drum_hit(0.05, amplitude=0.4)
    sfx.extend(generate_drum_hit(0.05, amplitude=0.35))
    sfx.extend(generate_drum_hit(0.05, amplitude=0.3))
    sfx.extend(generate_noise(0.05, amplitude=0.5))
    sfx.extend(generate_sine_wave(500, 0.1, amplitude=0.3))
    audio["sfx_combo"] = samples_to_wav_base64(sfx)

    # 道具使用
    sfx = generate_filtered_noise(0.1, amplitude=0.2, cutoff=2000)
    sfx.extend(generate_sine_wave(600, 0.1, amplitude=0.15))
    sfx.extend(generate_sine_wave(800, 0.1, amplitude=0.15))
    audio["sfx_use_item"] = samples_to_wav_base64(sfx)

    # 传送音效
    sfx = []
    for i in range(20):
        freq = 200 + i * 50
        sfx.extend(generate_sine_wave(freq, 0.05, amplitude=0.1 + i * 0.01))
    sfx.extend(generate_filtered_noise(0.3, amplitude=0.2, cutoff=3000))
    audio["sfx_teleport"] = samples_to_wav_base64(sfx)

    # 炼丹音效
    sfx = generate_filtered_noise(0.2, amplitude=0.15, cutoff=800)
    sfx.extend(generate_sine_wave(440, 0.15, amplitude=0.2))
    sfx.extend(generate_sine_wave(554, 0.15, amplitude=0.2))
    sfx.extend(generate_bell(659, 0.4, amplitude=0.1))
    audio["sfx_alchemy"] = samples_to_wav_base64(sfx)

    # 拍卖音效
    sfx = generate_bell(800, 0.2, amplitude=0.15)
    sfx.extend(generate_bell(1000, 0.2, amplitude=0.12))
    sfx.extend(generate_bell(1200, 0.3, amplitude=0.1))
    audio["sfx_auction"] = samples_to_wav_base64(sfx)

    # 宗门音效
    sfx = generate_bell(523, 0.3, amplitude=0.15)
    sfx.extend(generate_bell(659, 0.3, amplitude=0.12))
    sfx.extend(generate_bell(784, 0.3, amplitude=0.1))
    sfx.extend(generate_chord([523, 659, 784], 0.5, amplitude=0.08))
    audio["sfx_sect"] = samples_to_wav_base64(sfx)

    return audio

if __name__ == "__main__":
    print("生成游戏音频...")
    audio = generate_all_audio()

    # 生成JS代码
    js_code = "// 自动生成的游戏音频（base64编码的WAV文件）\n"
    js_code += "const GAME_AUDIO = {\n"
    for name, data in audio.items():
        js_code += f'    "{name}": "{data}",\n'
    js_code += "};\n\n"
    js_code += """
// 音频管理器
class AudioManager {
    constructor() {
        this.audioCtx = null;
        this.buffers = {};
        this.bgmSource = null;
        this.bgmGain = null;
        this.sfxGain = null;
        this.bgmVolume = 0.3;
        this.sfxVolume = 0.5;
        this.muted = false;
        this.loaded = false;
    }

    async init() {
        try {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            this.bgmGain = this.audioCtx.createGain();
            this.bgmGain.gain.value = this.bgmVolume;
            this.bgmGain.connect(this.audioCtx.destination);
            this.sfxGain = this.audioCtx.createGain();
            this.sfxGain.gain.value = this.sfxVolume;
            this.sfxGain.connect(this.audioCtx.destination);
            await this._loadAll();
            this.loaded = true;
        } catch (e) {
            console.warn('Audio init failed:', e);
        }
    }

    async _loadAll() {
        for (const [name, b64] of Object.entries(GAME_AUDIO)) {
            try {
                const binary = atob(b64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                this.buffers[name] = await this.audioCtx.decodeAudioData(bytes.buffer);
            } catch (e) {
                // skip failed audio
            }
        }
    }

    playSfx(name) {
        if (!this.loaded || this.muted || !this.buffers[name]) return;
        try {
            const source = this.audioCtx.createBufferSource();
            source.buffer = this.buffers[name];
            source.connect(this.sfxGain);
            source.start(0);
        } catch (e) {}
    }

    playBgm(name) {
        if (!this.loaded || !this.buffers[name]) return;
        this.stopBgm();
        try {
            this.bgmSource = this.audioCtx.createBufferSource();
            this.bgmSource.buffer = this.buffers[name];
            this.bgmSource.loop = true;
            this.bgmSource.connect(this.bgmGain);
            this.bgmSource.start(0);
        } catch (e) {}
    }

    stopBgm() {
        if (this.bgmSource) {
            try { this.bgmSource.stop(); } catch (e) {}
            this.bgmSource = null;
        }
    }

    setBgmVolume(v) { this.bgmVolume = v; if (this.bgmGain) this.bgmGain.gain.value = v; }
    setSfxVolume(v) { this.sfxVolume = v; if (this.sfxGain) this.sfxGain.gain.value = v; }
    toggleMute() { this.muted = !this.muted; if (this.bgmGain) this.bgmGain.gain.value = this.muted ? 0 : this.bgmVolume; }
}

const audioManager = new AudioManager();
"""

    with open("static/audio_data.js", "w", encoding="utf-8") as f:
        f.write(js_code)

    total_size = len(js_code)
    print(f"音频数据生成完成！")
    print(f"audio_data.js 大小: {total_size} 字节 ({total_size/1024:.0f}KB)")
    print(f"音频数量: {len(audio)}")
