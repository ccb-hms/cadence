"""
Tools for creating weekly meetings
Core for Computational Biomedicine at Harvard Medical School
Created in 2024 by Andreas Werdich
"""

import pandas as pd
import timeboard as tb
import holidays

def merge_alternatively(lst1, lst2):
    if not lst1:
        return lst2
    if not lst2:
        return lst1
    return [lst1[0], lst2[0]] + merge_alternatively(lst1[1:], lst2[1:])

def cyclic_lst(lst, d):
    return lst[d:] + lst[:d]

def cyclic_permutate(lst_in, name):
    lst_out = lst_in.copy()
    try:
        lst_in_low = [name.lower() for name in lst_in]
        idx = lst_in_low.index(name.lower())
        lst_out = cyclic_lst(lst=lst_in, d=idx)
    except ValueError:
        print(f'Name "{name}" is not in list.')
    return lst_out

def in_list(lst, elements):
    """ Return true only if all elements are in the list lst """
    check_lst = [True if el in lst else False for el in elements]
    return all(check_lst)

class Meetings:
    def __init__(self, name_df, meeting_day=2):
        self.name_df = name_df
        self.meeting_day = meeting_day
        self.col_dict = {'date_col': 'date',
                         'name_col': 'name',
                         'comment_col': 'comment',
        }

    def presenter_list(self, group_col='group', random_state=123):
        presenters_df = self.name_df.sample(frac=1, random_state=random_state)
        group_list = presenters_df[group_col].unique()
        name_col = self.col_dict.get('name_col')
        name_lists = [sorted(list(presenters_df.loc[presenters_df.get(group_col) == grp, name_col].values)) \
                      for grp in group_list]
        # This only works when we have two groups.
        # ToDo: Make it work for more than two groups
        presenters = merge_alternatively(name_lists[0], name_lists[1])
        return presenters

    def skip_date(self, cal_df, skip_date, skip_comment):
        date_col = self.col_dict.get('date_col')
        name_col = self.col_dict.get('name_col')
        comment_col = self.col_dict.get('comment_col')
        cal_df_skip = cal_df.loc[cal_df.get(date_col) == skip_date]
        cal_df_skip.loc[cal_df_skip.get(date_col) == skip_date, comment_col] = skip_comment
        if len(cal_df_skip) > 0:
            cal_df_before = cal_df.loc[cal_df.get(date_col) < skip_date]
            cal_df_after = cal_df.loc[cal_df.get(date_col) > skip_date]
            name_list = list(cal_df.get(name_col).unique())
            # Re-create the calendar for the dates after the skip date
            cal_df_after = self.create_timeboard(start_date=cal_df_after[date_col].min(),
                                                 end_date=cal_df_after[date_col].max(),
                                                 start_name=cal_df_skip.get('name').values[0])
            cal_df = pd.concat([cal_df_before, cal_df_skip, cal_df_after], axis=0, ignore_index=True)
        else:
            raise ValueError(f'Skip date {skip_date} is not in data.')
        return cal_df

    def swap_dates(self, cal_df, date_1, date_2):
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

    def create_timeboard(self, start_date, end_date, start_name, name_list=None):
        us_ma_holidays = holidays.country_holidays('US', subdiv='MA')
        # Create a list of name from the table of names
        if name_list is None:
            name_list = list(self.name_df[self.col_dict.get('name_col')].unique())
        # Rotate the speakers so that the start_name comes first
        nlist = cyclic_permutate(lst_in=name_list, name=start_name)
        # Define the list of speakers
        team_order = tb.RememberingPattern(nlist)
        # Set a weekly marker for every Wednesday
        week_day = tb.Marker(each='W', at=[{'days': self.meeting_day}])
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

        return cal


def main():
    print("Hello World!")

if __name__ == "__main__":
    main()