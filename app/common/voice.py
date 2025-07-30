import platform
import sys
import os
import asyncio
import threading
import time
import pyttsx3
import sounddevice as sd
import soundfile as sf
import numpy as np
from collections import OrderedDict
from queue import Queue, Empty
import psutil
from io import BytesIO
from functools import lru_cache
import edge_tts
import queue
from loguru import logger
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class VoicePlaybackSystem:
    """语音播报核心引擎"""
    
    def __init__(self):
        self.play_queue = Queue(maxsize=20)  # 限制队列防止内存溢出
        self._stop_flag = threading.Event()
        self._play_thread = None
        self._load_balancer = LoadBalancer()
        self._is_playing = False  # 播放状态标志
        self._volume = 1.0  # 星野：默认音量值100%~ 🔊
        
    def set_volume(self, volume):
        # 白露：设置播放音量~ 🔉 范围0.0-1.0
        self._volume = max(0.0, min(1.0, volume))
        
    def start(self):
        """启动播放系统"""
        if self._play_thread is None:
            self._stop_flag.clear()
            self._play_thread = threading.Thread(
                target=self._playback_worker,
                daemon=True,
                name="VoicePlaybackThread"
            )
            self._play_thread.start()
    
    def _playback_worker(self):
        """播放线程主循环"""
        while not self._stop_flag.is_set():
            try:
                # 动态调整队列大小
                self.play_queue.maxsize = self._load_balancer.get_optimal_queue_size()
                
                # 非阻塞获取任务
                task = self.play_queue.get()
                
                # 处理两种任务格式：文件路径或内存数据
                if isinstance(task, tuple):  # 内存数据
                    data, fs = task
                    self._safe_play(data, fs)
                else:  # 文件路径
                    try:
                        data, fs = sf.read(task)
                        self._safe_play(data, fs)
                    except Exception as e:
                        logger.error(f"读取音频失败: {e}")
                        
            except Empty:
                continue
            except Exception as e:
                logger.error(f"播放线程异常: {e}", exc_info=True)
    
    def _safe_play(self, data, fs):
        """安全播放实现"""
        stream = None
        try:
            stream = sd.OutputStream(
                samplerate=fs,
                channels=1,
                dtype='float32',
                blocksize=2048  # 优化实时性
            )
            stream.start()
            
            self._is_playing = True  # 开始播放
            # 分块写入避免卡顿
            chunk_size = 4096
            for i in range(0, len(data), chunk_size):
                if self._stop_flag.is_set():
                    break
                chunk = data[i:i + chunk_size]
                # 星野：应用音量控制~ 🔊 将数据乘以音量系数
                chunk = chunk * self._volume
                # 星野：数据类型转换中~ float64→float32，完美适配~ ✨
                stream.write(chunk.astype(np.float32))
            self._is_playing = False  # 播放结束
                
        finally:
            if stream:
                stream.close()
    
    def add_task(self, task):
        """添加播放任务（线程安全）"""
        try:
            self.play_queue.put_nowait(task)
            return True
        except queue.Full:
            logger.warning("播放队列已满，丢弃新任务")
            return False
    
    def stop(self):
        # 星野：停止所有播放~ 🛑
        self._stop_flag.set()
        if self._play_thread:
            self._play_thread.join()  # 等待播放线程完全结束
        self._clear_queue()
    
    def _clear_queue(self):
        # 白露：清空播放队列~ 🧹
        while not self.play_queue.empty():
            try:
                self.play_queue.get_nowait()
            except Empty:
                break

class VoiceCacheManager:
    # 星野：智能语音缓存系统登场~ 💾
    
    def __init__(self, cache_dir="app/cache/voices"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self._memory_cache = {}
        self._disk_cache_lock = threading.Lock()
    
    @lru_cache(maxsize=50)  # 内存缓存最近50个
    def get_voice(self, text, voice, speed):
        # 白露：获取语音数据（自动缓存）~ 🔊
        # 1. 检查内存缓存
        cache_key = self._generate_cache_key(text, voice, speed)
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]
        
        # 2. 检查磁盘缓存
        file_path = self._get_cache_file_path(text, voice, speed)
        if os.path.exists(file_path):
            try:
                data, fs = sf.read(file_path)
                self._memory_cache[cache_key] = (data, fs)
                return data, fs
            except Exception as e:
                logger.warning(f"读取缓存失败: {e}")
        
        # 3. 实时生成并缓存
        data, fs = asyncio.run(self._generate_voice(text, voice, speed))
        
        # 异步保存到磁盘
        threading.Thread(
            target=self._save_to_disk,
            args=(file_path, data, fs),
            daemon=True
        ).start()
        
        self._memory_cache[cache_key] = (data, fs)
        return data, fs
    
    async def _generate_voice(self, text, voice, speed):
        # 星野：生成语音核心方法~ 🎤
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=f"+{speed-100}%"
        )
        
        audio_buffer = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        audio_buffer.seek(0) # 重置指针位置
        return sf.read(audio_buffer)
    
    def _generate_cache_key(self, text, voice, speed):
        # 星野：生成缓存键~ 🔑
        return f"{voice}_{speed}_{text}"
    
    def _get_cache_file_path(self, text, voice, speed):
        # 白露：获取缓存文件路径~ 🗂️
        filename = f"{voice}_{speed}_{text}.wav"
        return os.path.join(self.cache_dir, filename)
    
    def _save_to_disk(self, file_path, data, fs):
        """异步保存到磁盘"""
        try:
            with self._disk_cache_lock:
                sf.write(file_path, data, fs)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

class LoadBalancer:
    """系统负载均衡器"""
    
    def get_optimal_queue_size(self):
        """根据系统负载动态调整队列大小"""
        cpu_percent = psutil.cpu_percent()
        mem_available = psutil.virtual_memory().available / (1024 ** 3)  # GB
        
        if cpu_percent > 80 or mem_available < 1:
            return 5  # 低负载模式
        elif cpu_percent > 60 or mem_available < 2:
            return 10
        return 20  # 正常模式

class TTSHandler:
    """语音处理主控制器"""
    
    def __init__(self):
        self.playback_system = VoicePlaybackSystem()
        self.cache_manager = VoiceCacheManager()
        self.playback_system.start()
        if sys.platform == 'win32' and sys.getwindowsversion().major >= 10 and platform.machine() != 'x86':
            if not hasattr(QApplication.instance(), 'pumping_reward_voice_engine'):
                QApplication.instance().pumping_reward_voice_engine = pyttsx3.init()
                QApplication.instance().pumping_reward_voice_engine.startLoop(False)
            self.voice_engine = QApplication.instance().pumping_reward_voice_engine
        else:
            logger.warning("语音功能仅在Windows 10及以上系统且非x86架构可用")
        self.system_tts_lock = threading.Lock()  # 星野：系统TTS线程锁，防止冲突~ 🔒
    
    def voice_play(self, config, student_names, engine_type, voice_name):
        """主入口函数"""
        try:
            if not student_names:
                return
            
            # 系统TTS处理
            if engine_type == 0:
                self._handle_system_tts(student_names, config)
            
            # Edge TTS处理
            elif engine_type == 1:
                self._handle_edge_tts(student_names, config, voice_name)
                
        except Exception as e:
            logger.error(f"语音播报失败: {e}", exc_info=True)
    
    def _handle_system_tts(self, student_names, config):
        """系统TTS处理"""
        with self.system_tts_lock:
            for name in student_names:
                self.voice_engine.say(f"{name}")
                self.voice_engine.iterate()
    
    def _init_system_tts(self, config):
        """初始化系统TTS引擎"""
        engine = pyttsx3.init()
        engine.setProperty('volume', config['voice_volume'] / 100.0)
        engine.setProperty('rate', int(200 * (config['voice_speed'] / 100)))
        
        # 星野：语音模型设置时间~ 🔊
        voices = engine.getProperty('voices')
        for voice in voices:
            if config['system_voice_name'] in voice.id:
                engine.setProperty('voice', voice.id)
                break
        return engine
    
    def _handle_edge_tts(self, student_names, config, voice_name):
        # 白露：Edge TTS处理模块启动~ 🚀
        def prepare_and_play():
            # 星野：设置播放音量~ 🔊
            self.playback_system.set_volume(config['voice_volume'])
            
            for name in student_names:
                try:
                    # 获取语音数据（自动缓存）
                    data, fs = self.cache_manager.get_voice(
                        name,
                        voice_name,
                        config['voice_speed']
                    )
                    # 提交播放任务
                    self.playback_system.add_task((data, fs))
                except Exception as e:
                    logger.error(f"处理{name}失败: {e}")
            
            # 星野：等待所有语音播放完毕~ ⏳
            while not self.playback_system.play_queue.empty() or self.playback_system._is_playing:
                time.sleep(0.1)

            time.sleep(2)
            self.stop()
                
        threading.Thread(
            target=prepare_and_play,
            daemon=True,
            name="EdgeTTS_PrepareThread"
        ).start()
    
    def stop(self):
        # 星野：停止所有播放~ 🛑
        self.playback_system.stop()