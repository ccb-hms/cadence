"""
Tools for creating weekly meetings
Core for Computational Biomedicine at Harvard Medical School
Created in 2024 by Andreas Werdich
"""
from __future__ import annotations

import argparse
import pandas as pd
import timeboard as tb
import holidays
import logging
import operator
from functools import reduce
from itertools import chain

logger = logging.getLogger(__name__)

def cyclic_lst(lst: list, d: int) -> list:
    """
    This function takes a list `lst` and an integer `d` as input parameters.
    It returns a new list by rotating the elements of `lst` to the right by `d` positions.

    :param lst: The list to be rotated.
    :param d: The number of positions to rotate the list by.
    :return: A new list with the elements of `lst` rotated to the right by `d` positions.
    """
    return lst[d:] + lst[:d]

def cyclic_permutate(lst_in: list, name: str) -> list:
    """
    Function that performs a cyclic permutation on a given list.

    :param lst_in: The input list that will be permuted.
    :param name: The name that will be used to determine the cyclic permutation.
    :return: The permuted list after performing the cyclic permutation.

    Example:
        lst_in = [1, 2, 3, 4, 5]
        name = "3"
        result = cyclic_permutate(lst_in, name)
        # result = [3, 4, 5, 1, 2]
    """
    lst_out = lst_in.copy()
    try:
        lst_in_low = [name.lower() for name in lst_in]
        idx = lst_in_low.index(name.lower())
        lst_out = cyclic_lst(lst=lst_in, d=idx)
    except ValueError:
        print(f'Name "{name}" is not in list.')
    return lst_out

def in_list(lst: list, elements: list) -> bool:
    """
    Determines if all elements in a given list are present in another list.

    :param lst: The list to check if elements are present in.
    :param elements: The list of elements to check for presence in `lst`.
    :return: Returns `True` if all elements in `elements` are present in `lst`, otherwise returns `False`.
    """
    check_lst = [True if el in lst else False for el in elements]
    return all(check_lst)

class Meetings:
    """
    Class for managing meetings and presenters.

    Args:
        name_list (list): A list of names.
        group_list (list, optional): A list of corresponding groups for names.

    Attributes:
        name_list (list): A list of names.
        col_dict (dict): A dictionary mapping column labels to column names.
        group_list (list): A list of corresponding groups for names.
        name_df (pd.DataFrame): A DataFrame containing the names and groups.

    Methods:
        create_name_df(name_list, group_list): Create a DataFrame from the name and group lists.
        merge_lists(list_of_lists): Merge a list of lists into a single list.
        create_name_sequence(name_sequence, merge_groups): Create a sequence of names.
        skip_date(cal_df, date, comment, name): Skip a date in the calendar DataFrame.
        swap_dates(cal_df, date_1, date_2): Swap two dates in the calendar DataFrame.
        create_timeboard(start_date, end_date, start_name, meeting_day): Create a timeboard DataFrame.
    """
    def __init__(self, name_list: list, group_list=None):
        self.name_list = name_list
        self.col_dict = {'date_col': 'date',
                         'group_col': 'group',
                         'name_col': 'name',
                         'comment_col': 'comment'}
        self.group_list = group_list
        self.name_df = self.create_name_df(self.name_list, self.group_list)

    def create_name_df(self, name_list: list, group_list: list) -> pd.DataFrame:
        name_df = pd.DataFrame({self.col_dict.get('name_col'): name_list})
        if group_list is not None:
            try:
                name_df[self.col_dict.get('group_col')] = group_list
            except ValueError as e:
                logger.error(f'Need {len(name_list)} groups, but got {len(group_list)}.')
        return name_df

    @staticmethod
    def merge_lists(list_of_lists: list) -> list:
        """
        Merges a list of lists into a single list.

        :param list_of_lists: The list of lists to be merged.
        :return: The merged list.
        """
        flattened = list(chain(*list_of_lists))
        merged = list(reduce(operator.add, zip(*list_of_lists)))
        # Add missing names at the end of the merged list
        merged.extend([name for name in flattened if name not in merged])
        return merged

    def create_name_sequence(self, name_sequence=None, merge_groups=True) -> list:
        """
        Creates a sequence of presenters

        :param name_sequence:   A list containing a specific sequence of names to be used for reordering the data frame.
                                Default is None.
        :param merge_groups: A boolean indicating whether to merge groups of names or not. Default is True.
        :return: A list containing the names in the new sequence.

        This method is used to create a new sequence of names for reordering the data frame.
        It takes an optional name_sequence parameter, which allows the user to specify a specific sequence of names.
        If name_sequence is not provided, the method uses the default sequence obtained from the data frame.
        If merge_groups is True and there are groups of names, the method merges the groups into a single list of names.
        This is done by iterating through the unique groups in the data frame and
        appending the names belonging to each group to a new list.
        After obtaining the new sequence of names, the method reorders the data frame based on this sequence.
        It creates a copy of the original data frame, sets the index to the name column,
        and then reindexes the data frame using the new sequence of names.
        Finally, it resets the index and returns the new sequence of names as a list.

        """
        presenter_list = list(self.name_df[self.col_dict.get('name_col')].values)
        if name_sequence is not None:
            presenter_list = [name for name in name_sequence if name in presenter_list]
        if self.group_list is not None and merge_groups:
            named_group_list = []
            name_col, group_col = self.col_dict.get('name_col'), self.col_dict.get('group_col')
            for group in self.name_df.get(group_col).unique():
                named_group_list.\
                    append(list(self.name_df.loc[self.name_df[group_col] == group, name_col].values))
            presenter_list = self.merge_lists(list_of_lists=named_group_list)
        # With the new sequence of names, we can re-order the data frame
        name_df = self.name_df.copy()
        name_df.index = name_df.get(self.col_dict.get('name_col'))
        self.name_df = name_df.reindex(index=presenter_list).reset_index(drop=True)
        return presenter_list

    def skip_date(self, cal_df: pd.DataFrame, date: str, comment: str, name='Everyone') -> pd.DataFrame:
        """
        Skip a date in the calendar DataFrame.

        :param cal_df: A pandas DataFrame representing a calendar.
        :param date: A string representing the date to skip.
        :param comment: A string representing the comment to add for the skipped date.
        :param name: A string representing the name to assign for the skipped date. Default value is 'Everyone'.
        :return: A pandas DataFrame representing the modified calendar.

        This method modifies the provided calendar DataFrame by skipping a specific date.
        It updates the comment and name columns for the skipped date,
        and re-creates the calendar for the dates after the skipped date.
        If the skipped date is not found in the calendar, a ValueError is raised.
        """
        date_col = self.col_dict.get('date_col')
        name_col = self.col_dict.get('name_col')
        comment_col = self.col_dict.get('comment_col')
        cal_df_skip = cal_df.loc[cal_df.get(date_col) == date]
        cal_df_skip.loc[cal_df_skip.get(date_col) == date, comment_col] = comment
        if len(cal_df_skip) > 0:
            cal_df_before = cal_df.loc[cal_df.get(date_col) < date]
            cal_df_after = cal_df.loc[cal_df.get(date_col) > date]
            # Re-create the calendar for the dates after the skip date
            cal_df_after = self.create_timeboard(start_date=cal_df_after[date_col].min(),
                                                 end_date=cal_df_after[date_col].max(),
                                                 start_name=cal_df_skip.get('name').values[0])
            cal_df_skip.loc[cal_df_skip.get(date_col) == date, name_col] = name
            cal_df = pd.concat([cal_df_before, cal_df_skip, cal_df_after], axis=0, ignore_index=True)
        else:
            raise ValueError(f'Skip date {date} is not in data.')
        return cal_df

    def swap_dates(self, cal_df: pd.DataFrame, date_1: str, date_2: str) -> pd.DataFrame:
        """
        Swaps the dates of two rows in a given pandas DataFrame.

        :param cal_df: The pandas DataFrame containing the calendar data.
        :param date_1: The first date to swap.
        :param date_2: The second date to swap.
        :return: The modified pandas DataFrame with the dates swapped.

        This function takes a pandas DataFrame,
        `cal_df`, along with two date strings, `date_1` and `date_2`,
        and swaps the dates of the corresponding rows in the DataFrame.
        The function returns a modified DataFrame with the dates swapped.
        """
        cal_df_new = cal_df.copy()
        # Convert the dates to datetime objects
        lst_dt = [pd.to_datetime(date_1), pd.to_datetime(date_2)]
        # Check if dates in the table
        check_dates = in_list(lst=cal_df_new['date'].values, elements=lst_dt)
        if check_dates:
            # Make copies of the rows we want to swap and then swap the dates.
            df0 = cal_df_new.loc[cal_df_new['date'] == lst_dt[0]]
            df0.loc[df0['date'] == lst_dt[0], 'date'] = lst_dt[1]
            df1 = cal_df_new.loc[cal_df_new['date'] == lst_dt[1]]
            df1.loc[df1['date'] == lst_dt[1], 'date'] = lst_dt[0]
            # Remove rows with the old dates
            cal_df_new.drop(cal_df_new.loc[cal_df_new['date'].isin(lst_dt)].index, inplace=True)
            # Add the changed rows back in
            cal_df_new = pd.concat([df0, df1, cal_df_new], axis=0). \
                sort_values(by='date', ascending=True). \
                reset_index(drop=True)
        return cal_df_new

    def create_timeboard(self, start_date: str, end_date: str, start_name=None, meeting_day=2) -> pd.DataFrame:
        """
        This method creates the meeting schedule using the timeboard library.

        :param self: The instance of the class.
        :param start_date: The start date of the time board.
        :param end_date: The end date of the time board.
        :param start_name: The name of the speaker to be rotated to the start.
        :param meeting_day: The day of the week for the meetings (default is Wednesday, represented by 2).
        :return: The created time board DataFrame.
        """
        us_ma_holidays = holidays.country_holidays('US', subdiv='MA')
        # Rotate the speakers so that the start_name comes first
        nlist = list(self.name_df[self.col_dict.get('name_col')].values)
        if start_name is not None:
            nlist = cyclic_permutate(lst_in=list(self.name_df[self.col_dict.get('name_col')].values), name=start_name)
        # Define the list of speakers
        team_order = tb.RememberingPattern(nlist)
        # Set a weekly marker for every Wednesday
        week_day = tb.Marker(each='W', at=[{'days': meeting_day}])
        weekly = tb.Organizer(marker=week_day, structure=team_order)
        cal = tb.Timeboard(base_unit_freq='D', start=start_date, end=end_date, layout=weekly)
        cal = cal.to_dataframe()
        cal = cal.reset_index(drop=True)[['start', 'label']]. \
            rename(columns={'start': self.col_dict.get('date_col'),
                            'label': self.col_dict.get('name_col')})

        # Merge with the other member information
        cal = cal.merge(right=self.name_df, on=self.col_dict.get('name_col'), how='left')

        # Add the MA holidays to this data frame
        cal = cal.assign(holiday=cal.get('date').apply(lambda dt: dt in us_ma_holidays),
                         comment=cal.get('date').apply(lambda dt: us_ma_holidays.get(dt)))

        # Convert the date to the pandas datetime type
        cal = cal.astype({self.col_dict.get('date_col'): 'datetime64[ns]'})

        return cal


def main():
    msg = 'Create a meeting schedule from a list of names.'
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('-n', '--names', help='"names, separated by commas"')
    parser.add_argument('-s', '--start', help='start date (str)')
    parser.add_argument('-e', '--end', help='end date (str)')
    args = parser.parse_args()
    names = args.names.split(',')
    # Remove space before the names
    names = [name.lstrip() for name in names]
    cal = Meetings(name_list=names).create_timeboard(start_date=args.start, end_date=args.end)
    # Print the schedule (we could also save it, but here, just show it
    print(cal)

if __name__ == '__main__':
    main()