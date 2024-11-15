import sys
import pyaudiowpatch as pyaudio
import wave
from youtube_logger import YoutubeLogger


class AudioRecorder:
    def __init__(self):
        self.youtube_logger = YoutubeLogger(file_path="log_script.log", file_name="log_script.log")
        # Set parameters
        self.duration = 30  # Duration in seconds
        self.chunk_size = 512
        self.filename = "loopback_record.wav"
        self.p = pyaudio.PyAudio()

        try:
            # Get default WASAPI info
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            "WASAPI is not available on the system. Exiting...")
            sys.exit(1)

        # Get default WASAPI speakers
        self.default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

        if not self.default_speakers["isLoopbackDevice"]:
            # Find a loopback device
            for loopback in self.p.get_loopback_device_info_generator():
                if self.default_speakers["name"] in loopback["name"]:
                    self.default_speakers = loopback
                    break
            else:
                self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                                "Default loopback output device not found.")
                sys.exit(1)

        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        f"Using device: {self.default_speakers['name']}")

    def record_audio(self):
        # Prepare wave file for saving the recording
        with wave.open(self.filename, 'wb') as wave_file:
            wave_file.setnchannels(self.default_speakers["maxInputChannels"])
            wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(int(self.default_speakers["defaultSampleRate"]))

            # Open the PyAudio stream
            with self.p.open(format=pyaudio.paInt16,
                             channels=self.default_speakers["maxInputChannels"],
                             rate=int(self.default_speakers["defaultSampleRate"]),
                             frames_per_buffer=self.chunk_size,
                             input=True,
                             input_device_index=self.default_speakers["index"]) as stream:
                # Calculate number of chunks
                num_chunks = int(int(self.default_speakers["defaultSampleRate"]) / self.chunk_size * self.duration)
                self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                                f"Recording {self.duration} seconds to {self.filename}")

                # Record audio in chunks
                for _ in range(num_chunks):
                    data = stream.read(self.chunk_size)
                    wave_file.writeframes(data)

        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        f"Recording saved as {self.filename}")
