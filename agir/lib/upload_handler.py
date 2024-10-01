## Custom Temporary file Upload Handlet to use if django settings
import os
import tempfile

from django.core.files.uploadedfile import UploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler


class PersistentTemporaryFileUploadHandler(TemporaryFileUploadHandler):

    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super().new_file(*args, **kwargs)
        self.file = PersistentTemporaryUploadedFile(
            self.file_name, self.content_type, 0, self.charset, self.content_type_extra
        )


class PersistentTemporaryUploadedFile(UploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """


def __init__(self, name, content_type, size, charset, content_type_extra=None):
    _, ext = os.path.splitext(name)
    file = tempfile.NamedTemporaryFile(suffix=".upload" + ext, delete=False)
    super().__init__(file, name, content_type, size, charset, content_type_extra)


def temporary_file_path(self):
    """Return the full path of this file."""
    return self.file.name


def close(self):
    try:
        return self.file.close()
    except FileNotFoundError:
        # The file was moved or deleted before the tempfile could unlink
        # it. Still sets self.file.close_called and calls
        # self.file.file.close() before the exception.
        pass
