import threading

import pyaudiowpatch as pyaudio
import wave
from youtube_logger import YoutubeLogger


class AudioRecorder:
    def __init__(self, youtube_logger: YoutubeLogger):
        """
        Initializes the audio recording setup using the PyAudio library and configures the audio input device for
        recording.

        :param youtube_logger: used for logging information
        :return: None
        """

        self.youtube_logger = youtube_logger
        # Duration in seconds
        self.duration = 120
        self.chunk_size = 1024
        self.filename = "audio_record.wav"
        self.p = pyaudio.PyAudio()

        try:
            # Get default WASAPI info
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
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

            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                            f"Using device: {self.default_speakers['name']}")
        except OSError:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            "WASAPI is not available on the system. Exiting...")

    def record_audio(self, stop_event: threading.Event):
        """
        Records audio from the selected input device for 120 seconds.
        The audio is recorded in chunks and saved as a .wav file.

        :param stop_event: a threading.Event used to signal when the recording should stop.
        :return: None
        """
        try:
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
                                                    f"Audio recording {self.duration} seconds to {self.filename}")

                    # Record audio in chunks
                    for _ in range(num_chunks):
                        # if the event is set, the recording stops
                        if stop_event.is_set():
                            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                                            "Audio recording stopped due to an event signal.")
                            break
                        data = stream.read(self.chunk_size)
                        # save the sound in file
                        wave_file.writeframes(data)
        except (OSError, PermissionError, wave.Error) as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"File or audio device error: {e}")
            raise
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Unexpected error: {e}")
            raise
        finally:
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                            f"Recording saved as {self.filename}")
