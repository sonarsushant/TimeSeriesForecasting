# functions
def create_date_features(data,name_of_ts_col,hour=False):
    """
    Create new features: year, month, day, weekday inplace in dataframe
    Param:
        data : dataframe
    """
    from datetime import datetime as dt
    
    data['Year']=data[name_of_ts_col].dt.year
    data['Month']=data[name_of_ts_col].dt.month
    data['Day']=data[name_of_ts_col].dt.day
    if hour == True:
        data['Hour']=data[name_of_ts_col].dt.hour
    data['Weekday']=data[name_of_ts_col].apply(lambda x: x.isoweekday())
    data['WeekOfMonth']=data[name_of_ts_col].apply(lambda d: (d.day-1) // 7 + 1)


# 1. Last n weekdays
def last_n_weekday_values(df,n=4):
    """
    This function will create n new columns with previous weekday value.
    
    e.g. For n=4, it will create 4 columns as 1 week prev value, 2 week prev value, etc.
    
    Params:
        n : int
    """
    for i in range(1,n+1):
        df['PrevWeek{}'.format(i)]=df.groupby('Weekday')['value'].shift(i)
    
    return df
        
# 2. Last month value of same weekday
def get_last_month_same_weekday_value(data):
    """
    This function will create new column 'PrevMonth' containing values of last month same week same weekday.
    
    e.g. For 2nd Monday of Feb, this column will have value of 2nd Monday of Jan
         If value of 2nd Monday is null, 1st Monday of Jan is considered.
         
    Params:
        data : dataframe containing date features. (Use create_date_features method before passing data)
    
    """
    import pandas as pd
    
    data_1=data.copy()

    data_1['Month']=data_1['Month']+1
    data_1.loc[data_1['Month']==13,'Year']=data_1[data_1['Month']==13]['Year']+1
    data_1['Month'].replace(13,1,inplace=True)

    data=pd.merge(data,data_1[['Year','Month','WeekOfMonth','Weekday','value']],how='left',
                  on=['Year','Month','WeekOfMonth','Weekday'])

    data=data.rename(columns={'value_x':'value','value_y':'PrevMonth'})

    #Replace null values by last month's previous week same weekday
    #e.g. if 5th Monday of March is missing, use 4th Monday of March

    null_index=data[data['PrevMonth'].isnull()].index

    data.loc[null_index,'PrevMonth']=\
        data.groupby('Weekday')['PrevMonth'].ffill().loc[null_index]
    
    return data
        
# 3. Prev Year value of same month same weekday
def get_last_year_same_month_same_weekday_value(data):
    """
    This function will create new column 'PrevYear' containing values of last year same month same weekday.
        
    e.g. For 2nd Monday of Feb 2011, this column will have value of 2nd Monday of Feb 2010.
         If 2nd Monday of Feb 2010 is null, 1st Monday of Feb 2010 is considered.
         
    Params:
        data= dataframe containing date features. (Use create_date_features method before passing data)
    
    """
    import pandas as pd
    
    data_1=data.copy()
    data_1['Year']=data_1['Year']+1
    data=pd.merge(data,data_1[['Year','Month','WeekOfMonth','Weekday','value']],how='left',
                  on=['Year','Month','WeekOfMonth','Weekday'])

    data=data.rename(columns={'value_x':'value','value_y':'PrevYear'})

    # If last year same week same weekday value is missing, replace it with last year previous week same weekday value
    # e.g. if 5th Monday of 2015 is missing, replace it with 4th Monday of 2015
    # e.g. if 1st Monday of 2015 is missing, replace it with 4th Monday of 2015

    null_index=data[data['PrevYear'].isnull()].index
    data.loc[null_index,'PrevYear']= data.groupby(['Month','Weekday'])['PrevYear'].ffill().loc[null_index]
    
    return data