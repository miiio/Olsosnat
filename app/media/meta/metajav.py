import os
import re

from config import RMT_MEDIAEXT
from app.media.meta._base import MetaBase
from app.utils import StringUtils
from app.utils.tokens import Tokens
from app.utils.types import MediaType
from app.media.meta.release_groups import ReleaseGroupsMatcher


class MetaJav(MetaBase):
    """
    识别Jav
    """
    # def __init__(self, title, subtitle=None, fileflag=False):
    def __init__(self, title, fh, cc=False, fileflag=False):
        super().__init__(title, fh, fileflag)
        if not fh:
            return
        self.title = fh
        self.org_string = title
        self.type = MediaType.JAV
        self.note.update({'cc': cc})