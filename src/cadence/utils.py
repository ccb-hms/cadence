"""
Some helper classes and methods for the cadence package
Core for Computational Biomedicine at Harvard Medical School
Created in 2024 by Andreas Werdich
"""

import random
import pandas as pd
import logging
from faker import Faker

logger = logging.getLogger(__name__)

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

