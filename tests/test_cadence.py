import pytest
import os
from tempfile import TemporaryDirectory
from cadence.utils import FileOP


__author__ = "Andreas Werdich"
__copyright__ = "Core for Computational Biomedicine at Harvard Medical School"
__license__ = "CC0-1.0"

def test_download():
    """ Download the CCB member file """
    group_members_file_name = 'ccb_members_2025.xlsx'
    url_base = 'https://dsets.s3.us-east-1.amazonaws.com'
    url = os.path.join(url_base, group_members_file_name)
    with TemporaryDirectory() as download_dir:
        file = FileOP().download_from_url(url=url, download_dir=download_dir, ext_list=['.xlsx'])
        assert os.path.basename(file) == group_members_file_name




