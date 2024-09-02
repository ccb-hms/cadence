"""
Some helper classes and methods for the cadence package
Core for Computational Biomedicine at Harvard Medical School
Created in 2024 by Andreas Werdich
"""

from __future__ import annotations

import os
import shutil
import contextlib
import traceback
import gzip
import random
import numpy as np
import pandas as pd
import logging
from urllib import request
from urllib.error import HTTPError
from faker import Faker
from tqdm import tqdm

logger = logging.getLogger(__name__)

class DownloadProgressBar(tqdm):
    """ Small helper class to make a download bar """
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class FileOP:
    """
    Class for file operations including downloading, extracting and file size checking.

    Parameters:
    - data_output_dir (Optional[str]): The directory to store the downloaded files.

    Attributes:
    - data_output_dir (str): The directory to store the downloaded files.
    - url (None or str): The URL of the file to download.

    Methods:
    - unzip(in_file: str, out_file: str) -> int: Unzips a .gz file and returns the file size.
    - file_size_from_url(url: str) -> int: Gets the size of a file without downloading it.
    - download_from_url(url: str, download_dir: str, extract: bool = True, delete_after_extract: bool = False, ext_list: Optional[List[str]] = None) -> str: Downloads a file from a URL and
    * returns the file path.

    """
    def __init__(self, data_output_dir=None):
        self.data_output_dir = data_output_dir
        self.url = None

    def unzip(self, in_file, out_file):
        """
        Unzip .gz file and return file size
        :param in_file: complete file path of compressed .gz file
        :param out_file: complete file path of output file
        :return: os.path.getsize(out_file) in bytes
        """
        if not os.path.isfile(out_file):
            try:
                with gzip.open(in_file, 'rb') as f_in, open(out_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            except Exception as e:
                logger.error(f'gzip failed on file: {in_file}: {e}')
                print(f'gzip failed on file: {in_file}: {e}')
                file_size = None
            else:
                file_size = os.path.getsize(out_file)
        else:
            print(f'Uncompressed output file exists: {out_file}. Skipping.')
            file_size = os.path.getsize(out_file)
        return file_size

    def file_size_from_url(self, url):
        """
        Method to acquire size of a file without download
        :param: url
        :returns: size in bytes (int)
        """
        url_size = np.nan
        try:
            with contextlib.closing(request.urlopen(url)) as ul:
                url_size = ul.length
        except HTTPError as http_err:
            logger.error(f'ERROR: {http_err}: URL: {url}')
        except Exception as e:
            logger.error(f'ERROR {e}: URL: {url}')
        return url_size

    def download_from_url(self, url, download_dir, extract=True, delete_after_extract=False, ext_list=None):
        """
        :param url: cloud storage location URL
        :param download_dir: path-like object representing file path.
        :param extract: extract file if compressed
        :param delete_after_extract: if file is an archive, delete file after extraction.
        :param ext_list: list of allowed extensions, for example '.json.gz' or '.zip'
        :return: file path of output file
        """
        output_file_name = os.path.basename(url)
        if ext_list is not None:
            ext_in_url = [xt for xt in ext_list if xt in url]
            if len(ext_in_url) > 0:
                xt = ext_in_url[0]
                output_file_name = f'{output_file_name.split(xt, maxsplit=1)[0]}{xt}'
        output_file = os.path.join(download_dir, output_file_name)
        if os.path.exists(download_dir):
            if not os.path.exists(output_file):
                try:
                    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=output_file_name) as t:
                        request.urlretrieve(url, filename=output_file, reporthook=t.update_to)
                except HTTPError as http_err:
                    print(http_err)
                    logger.error(f'Download failed for URL: {url}'
                                 f' {http_err}')
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f'Download failed for URL: {url}'
                                 f' {e}')
                else:
                    logger.info(f'Download complete: {output_file}.')
            else:
                logger.info(f'File exists: {output_file}')
            # Unpacking
            output_file_path = output_file
            if os.path.exists(output_file) and extract:
                file_parts = os.path.splitext(output_file)
                xt = file_parts[-1]
                if xt in ['.gz']:
                    print(f'Extracting from {xt} archive.')
                    out_file = file_parts[0]
                    file_size = self.unzip(in_file=output_file, out_file=out_file)
                    if file_size is not None:
                        output_file_path = out_file
                        if delete_after_extract:
                            os.unlink(output_file)
                            logger.info(f'Deleted compressed file {output_file}')
                elif xt in ['.json', '.csv', '.pickle', '.parquet', '.ckpt', '.pth']:
                    print(f'Created {xt} file.')
                else:
                    print(f'File: {xt} loaded.')
                    logger.warning(f'File extension is unexpected {xt}.')
            elif os.path.exists(output_file) and not extract:
                output_file_path = output_file
        else:
            logger.error(f'Output directory {download_dir} does not exist.')
            output_file_path = None
        return output_file_path

class GroupFaker:
    """

    The `GroupFaker` class is used to create random research groups with fake member names.
    It contains the following methods:

    - :meth:`__init__`: Initializes a new instance of the `GroupFaker` class.
    - :meth:`make_random_groups`: Creates random groups from a given list of members.
    - :meth:`create_fake_research_group`: Creates a DataFrame with fake research groups.

    """
    def __init__(self, n_members: int, n_groups: int, seed=123):
        self.n_members = n_members
        self.n_groups = n_groups
        self.fake = Faker()
        self.seed = seed
        Faker.seed(seed)

    def make_random_groups(self, member_list: list) -> list:
        """
        Make Random Groups

        This method takes a list of members and randomly assigns them to groups.

        :param member_list: A list of members to be assigned to groups.
        :return: A list of lists, where each inner list represents a group of members.

        Example Usage:
            >>> members = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
            >>> random_groups = self.make_random_groups(members)
            >>> print(random_groups)
            [['Charlie', 'Alice'], ['Eve', 'Bob'], ['David']]

        Note:
            - The number of groups is determined by the `n_groups` property of the object calling this method.
            - The order of the members in the input list is randomized before assigning them to groups.
            - If the number of members is not divisible by the number of groups, the last group may have fewer members.
        """
        random.seed(self.seed)
        random.shuffle(member_list)
        all_groups = []
        for index in range(self.n_groups):
            group = member_list[index::self.n_groups]
            all_groups.append(group)
        return all_groups

    def create_fake_research_group(self) -> pd.DataFrame:
        """
        Creates a fake research group with randomly assigned members.

        :return: A pandas DataFrame with the following columns:
                 - name: The full name of each member
                 - first_name: The first name of each member
                 - last_name: The last name of each member
                 - group: The group number to which each member is assigned
        """
        name_list = [self.fake.name() for n in range(self.n_members)]
        name_df = pd.DataFrame({'name': name_list})
        name_df[['first_name', 'last_name']] = name_df['name'].str.split(' ', expand=True)
        # Randomly assign members to groups
        name_df = name_df.assign(group=None)
        group_list = self.make_random_groups(member_list=name_df['name'].unique().tolist())
        for group in range(len(group_list)):
            name_df.loc[name_df['name'].isin(group_list[group]), 'group'] = f'group_{group}'
        name_df = name_df.sort_values(by=['group', 'name'], ascending=True).reset_index(drop=True)
        return name_df

