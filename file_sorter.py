import logging
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# folder to track e.g. Windows: "C:\\Users\\UserName\\Downloads"
source_dir = ""
dest_dir_sfx = ""
dest_dir_music = ""
dest_dir_video = ""
dest_dir_image = ""
dest_dir_documents = ""

image_extensions = [
    ".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw",
    ".arw", ".cr2", ".nrw", ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k",
    ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"
]
video_extensions = [
    ".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".mp4", ".mp4v",
    ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"
]
audio_extensions = [
    ".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"
]
document_extensions = [
    ".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"
]


def make_unique(dest: str, name: str) -> str:
    """ If file exists add number to the end of filename.

    :param dest: path to the file
    :param name: filename
    :return: new name
    """
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name


def move_file(dest: str, entry: str, name: str) -> None:
    """ Rename and move file.

    :param dest: path to the file
    :param entry:
    :param name:
    """
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        old_name = join(dest, name)
        new_name = join(dest, unique_name)
        rename(old_name, new_name)
    move(entry, dest)


class MoverHandler(FileSystemEventHandler):
    # ? THIS FUNCTION WILL RUN WHENEVER THERE IS A CHANGE IN "source_dir"
    # ? .upper is for not missing out on files with uppercase extensions
    def on_modified(self, event: FileSystemEvent) -> None:
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.move_audio_files(entry, name)
                self.move_video_files(entry, name)
                self.move_image_files(entry, name)
                self.move_document_files(entry, name)

    @staticmethod
    def move_audio_files(entry: str, name: str) -> None:
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 10_000_000 or "SFX" in name:  # ? 10Megabytes
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")

    @staticmethod
    def move_video_files(entry: str, name: str) -> None:
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move_file(dest_dir_video, entry, name)
                logging.info(f"Moved video file: {name}")

    @staticmethod
    def move_image_files(entry: str, name: str) -> None:
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                move_file(dest_dir_image, entry, name)
                logging.info(f"Moved image file: {name}")

    @staticmethod
    def move_document_files(entry: str, name: str) -> None:
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move_file(dest_dir_documents, entry, name)
                logging.info(f"Moved document file: {name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
