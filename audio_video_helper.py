from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment
import csv
from youtube_logger import YoutubeLogger


class AudioVideoHelper:
    def __init__(self, youtube_logger: YoutubeLogger):
        """
        Initializes the AudioVideoHelper class.

       :param youtube_logger: used for logging information
       :return: None
        """
        self.logger = youtube_logger

    def merge_audio_video(self):
        """
        Merges the audio and video into a final video file. The audio is trimmed to start from 1 second
        and then added to the video.

        :return: None
        """
        try:
            # Load video and audio
            self.logger.log_message(self.logger.Level.INFO.value, "Starting merge of audio and video.")
            video = VideoFileClip("output.avi")
            audio = AudioFileClip("audio_record.wav")

            # Start the audio from 1 second
            trimmed_audio = audio.subclip(1, audio.duration)

            # Set the audio to the video
            final_video = video.set_audio(trimmed_audio)
            self.logger.log_message(self.logger.Level.INFO.value, "Writing final video to file.")
            # Write the result to the output file
            final_video.write_videofile("final_output.mp4", codec="libx264", audio_codec="aac")
            self.logger.log_message(self.logger.Level.INFO.value, "Audio and video successfully merged into "
                                                                  "final_output.mp4.")
        except Exception as e:
            self.logger.log_message(self.logger.Level.ERROR.value,
                                    f"Error during merging audio and video: {e}")

    def write_db_to_file(self, avg_db, output_file="dB_levels.csv"):
        """
        Writes the average decibel (dB) level to a CSV file.

        :param avg_db: The average dB level to be written to the file.
        :param output_file: The name of the CSV file to write to (default is 'dB_levels.csv').
        :return: None
        """
        try:
            self.logger.log_message(self.logger.Level.INFO.value, f"Writing average dB level to {output_file}.")
            with open(output_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Header
                writer.writerow(["Average dB Level"])
                # Write the average dB level
                writer.writerow([avg_db])
            self.logger.log_message(self.logger.Level.INFO.value,
                                    f"Successfully wrote average dB level to {output_file}.")
        except Exception as e:
            self.logger.log_message(self.logger.Level.ERROR.value,
                                    f"Error during writing average dB level to file: {e}")

    def analyze_audio(self, audio_path, chunk_length_ms=1000):
        """
            Analyzes the audio from the given path by splitting it into chunks and calculating the average dB level.

            :param audio_path: Path to the audio file to be analyzed.
            :param chunk_length_ms: Length of each chunk in milliseconds (default is 1 second).
            :return: None
            """
        try:
            self.logger.log_message(self.logger.Level.INFO.value, f"Starting audio analysis for {audio_path}.")
            audio = AudioSegment.from_wav(audio_path)
            num_chunks = len(audio) // chunk_length_ms
            db_levels = []

            for i in range(num_chunks):
                # slice the audio
                chunk = audio[i * chunk_length_ms:(i + 1) * chunk_length_ms]
                db = chunk.dBFS
                # Ignore chunks with -inf dBFS
                if db > float('-inf'):
                    db_levels.append(db)

            # Calculate the average dB level
            avg_db = sum(db_levels) / len(db_levels) if db_levels else float('-inf')

            # Write the average dB level to the file
            self.write_db_to_file(avg_db)
            self.logger.log_message(
                self.logger.Level.INFO.value,
                f"Completed analysis for {audio_path}. Average dB level: {avg_db}"
            )
        except Exception as e:
            self.logger.log_message(
                self.logger.Level.ERROR.value,
                f"Error during audio analysis: {e}"
            )
