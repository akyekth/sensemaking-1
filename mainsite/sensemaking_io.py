import urllib3
import json
import urllib
import dateutil.parser as parser
from dateutil.parser import parse
from datetime import datetime

from sklearn.externals import joblib
from sqlalchemy import create_engine

import os

import pandas as pd

engine = create_engine('mysql://root:root@localhost:3306/twitterSchema')


def query_temp(sqlStmt, param=None, param1=None):
    if param is None:
        rs = pd.read_sql(sqlStmt, con=engine)
    else:
        rs = pd.read_sql(sqlStmt, con=engine, params=param)
    return rs.values.tolist()


def query(sqlStmt, param=None):
    if param is None:
        rs = pd.read_sql(sqlStmt, con=engine)
    else:
        rs = pd.read_sql(sqlStmt, con=engine, params=param)
    return rs.values.tolist()


def read_embedding():
    fn = 'final_mn3_mx50000_conf1024-900-768_s128_sd1976_dst-uniform_tr100_lr0001_rc001_user_delay_combined.emb'
    path = os.path.join('./sensemaking/data/emb/', fn)
    return pd.read_csv(path, header=None, sep='\s+', index_col=0, skiprows=1)


def load_model(obs_time, prd_time, th):
    print('virality threshold', th)
    path = './sensemaking/data/model/combined/mn3_mx50000_conf1024-900-768_s128_sd1976_' \
           'dst-uniform_tr100_lr0001_rc001_ot{}_pt{}_vt{}.mdl'.format(obs_time,
                                                                      obs_time + prd_time, th / 100.)
    return joblib.load(path)


def init_data(path=None, use_cols=None, sep='\t', sql=None):
    if sql is None:
        p = './sensemaking/data/input/hashtag_daily_sum.csv' if path is None else path
        if use_cols is not None:
            return pd.read_csv(p, sep=sep, usecols=use_cols)
        else:
            return pd.read_csv(p, sep=sep)
    else:
        return query(sql)


def load_tweet_data(path, sql, use_cols, sep):
    if sql is None:
        return init_data(path=path, use_cols=use_cols, sep=sep)
    else:
        return init_data(sql=sql)


def hashtags_in_window(path=None, sql=None, use_cols=None, sep='\t', obs_time=1, prd_time=1,
                       obs_min_size=5, prd_min_size=5):
    data = load_tweet_data(path=path, sql=sql, use_cols=use_cols, sep=sep)

    observation_data = data[data.relative_time <= obs_time * 3600]
    criteria = (data.relative_time > obs_time * 3600) & (data.relative_time <= prd_time * 3600)
    prediction_data = data[criteria]
    print(observation_data.head())
    observation_data = observation_data.groupby('hashtag').filter(lambda l: len(l) >= obs_min_size)
    prediction_data = prediction_data.groupby('hashtag').filter(lambda l: len(l) >= prd_min_size)
    print(observation_data.shape, prediction_data.shape)
    valid_data = observation_data.merge(prediction_data, on='hashtag')
    cols = ['hashtag', 'user_id_x', 'created_at_x', 'label_x', 'user_name_x', 'tweet_text_x',
            'tweet_id_x', 'tweet_id_x', 'timestamp_x', 'relative_time_x']
    valid_data = valid_data[cols]
    cols = ['hashtag', 'user_id', 'created_at', 'label', 'user_name', 'tweet_text',
            'tweet_id', 'tweet_id', 'timestamp', 'relative_time']
    valid_data.columns = cols
    return valid_data.sort_values('hashtag', ascending=False)


def hashtag_daily_summary(ht, start='2016-01-01', end='2016-12-31'):
    path = './sensemaking/data/input/hashtag_daily_sum.csv'
    print('Reading from {}'.format(path))
    df = init_data(path=path, sep=',')
    df = df.set_index('hashtag')
    ht_df = df.loc[ht][:]
    ht_df = ht_df[(ht_df.date >= start) & (ht_df.date <= end)]
    ht_df.reset_index(inplace=True)
    print(ht_df.head())
    print(ht_df.tail())
    return ht_df.sort_values(['hashtag', 'date']).values.tolist()


def user_daily_summary(path, user, key='user_name', start='2016-01-01', end='2016-12-31', sep='\t'):
    df = init_data(path=path, sep=sep)
    print(df.head())
    df = df.set_index(key)
    user_df = df.loc[user][:]
    user_df = user_df[(user_df.date >= start) & (user_df.date <= end)]
    user_df.reset_index(inplace=True)
    return user_df.sort_values(['user_name', 'date']).values.tolist()


def group_into_hashtags(df):
    g = df.groupby('hashtag')
    group_data = []
    for ht in g.groups:
        ht_df = g.get_group(ht)
        ht_df['hashtag'] = ht
        group_data.append([ht, ht_df.Count.values.tolist(), ht_df.Date.values.tolist()])
    return group_data


def hashtag_summary_pandas(hts, path=None):
    df = init_data(path=path)
    print('Computing summary')
    df.set_index('hashtag', inplace=True)
    temp_df = df.loc[hts]
    temp_df.reset_index(inplace=True)
    temp_df.created_at = pd.to_datetime(temp_df.created_at)
    temp_df.set_index('created_at', inplace=True)
    daily_stat = temp_df.groupby(['hashtag', lambda l: l.month, lambda l: l.day])['user_id'].count().to_frame()

    daily_stat.index.names = ['hashtag', 'month', 'day']
    daily_stat.reset_index(inplace=True)
    daily_stat['date'] = daily_stat.apply(lambda l: '2016-{}-{}'.format(l['month'], l['day']), axis=1)
    daily_stat = daily_stat.drop(['month', 'day'], axis=1)
    daily_stat.date = pd.to_datetime(daily_stat.date)
    daily_stat.columns = ['hashtag', 'Count', 'Date']
    print(daily_stat)
    if len(hts) == 1:
        dates = ['{}'.format(d) for d in daily_stat.Date.values]
        return dates, daily_stat.Count.values.tolist()
    else:
        return group_into_hashtags(daily_stat)


def hashtag_monthly_summary(top_k=10):
    path = './sensemaking/data/input/hashtag_monthly_summary.csv'
    df = init_data(path, sep=',')
    df = df[df['rank'] <= top_k]
    return df.values.tolist()


def list_of_hashtags():
    df = init_data()
    lst_of_lst = df.li.str.split(',').values
    return list(set([ht for lst in lst_of_lst for ht in lst]))


def prediction_detail(prediction):
    print("Inside details", prediction)
    virality_prob = prediction[1]
    non_virality_prob = prediction[0]
    if virality_prob > non_virality_prob:
        return 'Viral', virality_prob
    else:
        return 'Not-Viral', non_virality_prob


def topk_monthly_hashtag_summary():
    sqlstmt = "select * from cumulative where rank <='10'"
    res = query(sqlstmt)
    return res


def topk_monthly_hashtag_summary_tweet_distribution(ht):
    sqlstmt = "select `date`, tweet_count from cumulative_daily where hashtag=%(ht)s"
    q = query(sqlstmt, param={'ht': ht})
    print(q)
    return q


def topk_monthly_hashtag_summary_label_distribution(ht):
    # example query: select count(tweet_id),label,month(created_at) as month from twitter_data where hashtag='migpol' group by label,month;
    sqlstmt = "select count(tweet_id),label,month(created_at) as month from twitter_data where hashtag=%(ht)s group by label,month"
    return query(sqlstmt, param={'ht': ht})


def topk_monthly_hashtag_summary_user_rank_distribution(ht):
    # example query: select count(tweet_id),label,month(created_at) as month from twitter_data where hashtag='migpol' group by label,month;
    # select a.user_id,rank from (select user_id from twitter_data where hashtag='migpol')a inner join user_rank using(user_id)
    sqlstmt = "select a.user_id,rank from (select user_id from twitter_data where hashtag=%(ht)s)a inner join user_rank using(user_id)"
    return query(sqlstmt, param={'ht': ht})


def search_dailyhashtag_timebound_tweet_distribution(ht, date1, date2):
    # select user_count,tweet_count from cumulative_daily where hashtag='migpol'and date between '2016-03-01' and '2016-10-01';
    if date1 and date2 is not None:
        sqlstmt = "select user_count,tweet_count from cumulative_daily where hashtag=%(ht)s and date between %(date1)s and %(date2)s"
        return query(sqlstmt, param={'ht': ht, 'date1': date1, 'date2': date2})
    else:
        sqlstmt = "select user_count,tweet_count from cumulative_daily where hashtag=%(ht)s"
        return query(sqlstmt, param={'ht': ht})


def search_dailyhashtag_timebound_label_distribution(ht, date1, date2):
    # date1 and date2 is in format string example '2016-10'

    # select count(tweet_id),label,month(created_at) as month from twitter_data where hashtag='migpol' and created_at between '2016-03-01' and '2016-10-02' group by label,month;

    if date1 and date2 is not None:
        sqlstmt = "select count(tweet_id),label,month(created_at) as month from twitter_data where hashtag=%(ht)s and created_at between %(date1)s and %(date2)s group by label,month"
        return query(sqlstmt, param={'ht': ht, 'date1': date1, 'date2': date2})
    else:
        return topk_monthly_hashtag_summary_label_distribution(ht)


def search_dailyhashtag_timebound_userrank_distribution(ht, date1, date2):
    # select a.user_id,rank from (select user_id from twitter_data where hashtag='migpol' and created_at between '2016-03-01' and '2016-10-02')a inner join user_rank using(user_id);
    if date1 and date2 is not None:
        sqlstmt = "select a.user_id,rank from (select user_id from twitter_data where hashtag=%(ht)s and created_at between %(date1)s and %(date2)s)a inner join user_rank using(user_id)"
        return query(sqlstmt, param={'ht': ht, 'date1': date1, 'date2': date2})
    else:
        return topk_monthly_hashtag_summary_user_rank_distribution(ht)


def search_user_category_tweet_distribution(uname):
    # select * from twitter_data where user_name='kdmariafalth';
    if uname is not None:
        sqlstmt = "select * from twitter_data where user_name=%(uname)s "
        return query(sqlstmt, param={'uname': uname})


def search_user_category_label_distribution(uname):
    # select * from twitter_data where user_name='kdmariafalth';
    if uname is not None:
        # example query: select count(tweet_id),label,month(created_at) as month from twitter_data where hashtag='migpol' group by label,month;
        sqlstmt = "select * from twitter_data where user_name=%(uname)s"
        return query(sqlstmt, param={'uname': uname})

def number_of_tweets_per_hashtag(ht,date1=None, date2=None):
    """

    :param ht: hashtag list
    :return: count of tweets realted to hashtag
    """
    # for item in ht:
    #     pas="{},".format(item)
    # if date1 and date2 is not None:
    #      sqlstmt = "select count(DISTINCT tweet_id) from twitter_data where hashtag in({}) and created_at between %(date1)s and %(date2)s)".format(pas)
    #      res = query(sqlstmt, param={'date1': date1, 'date2': date2})
    # else:
    #     sqlstmt = "select count(DISTINCT tweet_id) from twitter_data where hashtag in ({})".format(pas)
    #     res = query(sqlstmt)

    pars = ""
    for p in ht.split(','):
        pars += "'{}'".format(p) if pars == '' else ",'{}'".format(p)

    if date1 and date2 is not None:
        # sqlstmt = "select count(distinct tweet_id) from twitter_data where hashtag=%(ht)s and created_at between %(date1)s and %(date2)s) "
        sqlstmt = "select count(distinct tweet_id) from twitter_data where hashtag in ({}) and " \
                  "created_at between %(date1)s and %(date2)s) ".format(pars)
        res = query(sqlstmt, param={'date1': date1, 'date2': date2})
    else:
        # sqlstmt = "select count(distinct tweet_id) from twitter_data where hashtag=%(ht)s "
        sqlstmt = "select count(distinct tweet_id) from twitter_data where hashtag in ({})".format(pars)
        # res = query(sqlstmt, param={'ht': ht})
        res = query(sqlstmt)
    return res[0][0]

def percentage_per_hashtag(ht,date1=None, date2=None):
    """
    :param ht: hashtag- 'svpol'
    :param date1: from date- optional '2016-03-01'
    :param date2: to -date:optional '2016-10-01'
    :return: percentage
    """
    #ex: select c1/c2 as percentage from (select count(tweet_id) as c1 from twitter_data where hashtag='migpol' and created_at between '2016-03-01' and '2016-10-02')a cross join (select count(tweet_id) as c2 from twitter_data where created_at between '2016-03-01' and '2016-10-02')b
    #ex2: select c1/c2 as percentage from (select count(tweet_id) as c1 from twitter_data where hashtag='migpol')a cross join (select count(tweet_id) as c2 from twitter_data)b
    pars = ""
    for p in ht.split(','):
        pars += "'{}'".format(p) if pars == '' else ",'{}'".format(p)

    if date1 and date2 is not None:
        # sqlstmt = "select c1/c2 as percentage from (select count(tweet_id) as c1 from twitter_data where hashtag=%(ht)s and created_at between %(date1)s and %(date2)s)a cross join (select count(tweet_id) as c2 from twitter_data where created_at between %(date1)s and %(date2)s)b"
        sqlstmt = "select c1/c2 as percentage from (select count(tweet_id) as c1 from " \
                  "twitter_data where hashtag in ({}) and created_at between %(date1)s " \
                  "and %(date2)s)a cross join (select count(tweet_id) as c2 from twitter_data " \
                  "where created_at between %(date1)s and %(date2)s)b".format(pars)
        # res = query(sqlstmt, param={'ht': ht, 'date1': date1, 'date2': date2})
        res = query(sqlstmt, param={'date1': date1, 'date2': date2})
    else:
        # sqlstmt="select c1/c2 as percentage from (select count(tweet_id) as c1 from twitter_data where hashtag=%(ht)s)a cross join (select count(tweet_id) as c2 from twitter_data)b"
        sqlstmt="select c1/c2 as percentage from (select count(tweet_id) as c1 from twitter_data " \
                "where hashtag in ({}) )a cross join (select count(tweet_id) as c2 from twitter_data)b".format(pars)
        # res = query(sqlstmt, param={'ht': ht})
        res = query(sqlstmt)
    return res[0][0]

def number_of_users_per_hashtag(ht, date1=None, date2=None):
    """

    :param ht:hashtag
    :return: count users per hashtag
    """

    pars = ""
    for p in ht.split(','):
        pars += "'{}'".format(p) if pars == '' else ",'{}'".format(p)

    if date1 and date2 is not None:
        # sqlstmt = "select count(distinct user_id) from twitter_data where hashtag=%(ht)s and created_at between %(date1)s and %(date2)s) "
        sqlstmt = "select count(distinct user_id) from twitter_data where hashtag in ({}) and " \
                  "created_at between %(date1)s and %(date2)s) ".format(pars)
        # res = query(sqlstmt, param={'ht': ht, 'date1': date1, 'date2': date2})
        res = query(sqlstmt, param={ 'date1': date1, 'date2': date2})
    else:
        # sqlstmt = "select count(distinct user_id) from twitter_data where hashtag=%(ht)s"
        sqlstmt = "select count(distinct user_id) from twitter_data where hashtag in ({})".format(pars)
        # res = query(sqlstmt, param={'ht': ht})
        res = query(sqlstmt)
    return res[0][0]


def top_k_users(k):
    sqlStmt = "select * from user_rank ORDER BY rank DESC limit {}".format(k)
    res = query(sqlStmt=sqlStmt)
    return list(zip(*res))[0]

def top_k_users_retweet_dist(users):
    path = './sensemaking/data/input/re_tweet_daily_sum.tsv'
    df = init_data(path=path)
    df = df.set_index('user_id')
    user_df = df.loc[users]
    return user_df.values.tolist()

# def tweet_text_input_based(ht=None,uname=None,uid=None,date1=None,date2=None):
#     """
#
#     :param ht: list of hahstags
#     :param uname:list of usernames
#     :param uid: list of user ids
#     :return: tweet_text realted to input
#     """
#     if ht is not None:
#         # param1=''
#         # for i in ht:
#         #     param1+="{},".format(i)
#         if date1 and date2 is not None:
#             # select tweet_text from twitter_data where hashtag='migpol'
#             sqlstmt = "select tweet_text from twitter_data where hashtag=%(ht)s and created_at between %(date1)s and %(date2)s)"
#             res = query(sqlstmt, param={'ht': ht,'date1': date1, 'date2': date2})
#         else:
#             sqlstmt = "select tweet_text from twitter_data where hashtag=%(ht)s"
#             res = query(sqlstmt,param={'ht': ht})
#
#
#     if uname is not None:
#         # param2 = ''
#         # for i in uname:
#         #     param2 += "{},".format(i)
#         if date1 and date2 is not None:
#             # select tweet_text from twitter_data where user_name='pensionarer' limit 10;
#             sqlstmt = "select tweet_text from twitter_data where user_name= %(uname)s and created_at between %(date1)s and %(date2)s)"
#             res = query(sqlstmt, param={'uname': uname,'date1': date1, 'date2': date2})
#         else:
#             sqlstmt = "select tweet_text from twitter_data where user_name= %(uname)s"
#             res = query(sqlstmt,param={'uname': uname})
#
#     if uid is not None:
#         # param2 = ''
#         # for i in uname:
#         #     param2 += "{},".format(i)
#         if date1 and date2 is not None:
#             # select tweet_text from twitter_data where user_name='pensionarer' limit 10;
#             sqlstmt = "select tweet_text from twitter_data where user_id== %(uid)d and created_at between %(date1)s and %(date2)s)"
#             res = query(sqlstmt, param={'uid': uid,'date1': date1, 'date2': date2})
#         else:
#             sqlstmt = "select tweet_text from twitter_data where user_id== %(uid)d"
#             res = query(sqlstmt,param={'uid': uid})
#     return res


def tweet_text_input_based(ht=None,uname=None,uid=None,date1=None,date2=None, users_of_ht=0):
    """

    :param ht: list of hahstags
    :param uname:list of usernames
    :param uid: list of user ids
    :return: tweet_text realted to input
    """
    print(uname)
    if ht is not None:
        param1=''
        for i in ht:
            param1 += "'{}'".format(i) if param1 == '' else ",'{}'".format(i)
        if date1 and date2 is not None:
            # select tweet_text from twitter_data where hashtag='migpol'
            sqlstmt = "select user_name, tweet_text from twitter_data where hashtag in ({}) and " \
                      "created_at between %(date1)s and %(date2)s)".format(param1)

            res = query(sqlstmt, param={'date1': date1, 'date2': date2})
        else:
            sqlstmt = "select user_name, tweet_text from twitter_data where hashtag in ({})".format(param1)

            res = query(sqlstmt)

    if uname is not None:
        param2 = ''
        if users_of_ht == 0:
            for i in uname:
                param2 += "'{}'".format(i) if param2 == '' else ",'{}'".format(i)
            if date1 and date2 is not None:
                # select tweet_text from twitter_data where user_name='pensionarer' limit 10;
                sqlstmt = "select user_name, tweet_text from twitter_data as t INNER JOIN " \
                          "followers_count_jsondata as f USING(user_id) where user_name in ({}) and" \
                          " created_at between %(date1)s and %(date2)s) ORDER BY f.followers_count DESC".format(param2)
                res = query(sqlstmt, param={'date1': date1, 'date2': date2})
            else:
                sqlstmt = "select user_name, tweet_text from twitter_data where user_name in ({})".format(param2)

        else:
            for i in uname:
                param2 += "'{}'".format(i) if param2 == '' else ",'{}'".format(i)
            if date1 and date2 is not None:
                # select tweet_text from twitter_data where user_name='pensionarer' limit 10;
                sqlstmt = "select user_name, tweet_text from twitter_data as t INNER JOIN " \
                          "followers_count_jsondata as f USING(user_id) where hashtag in ({}) and" \
                          " created_at between %(date1)s and %(date2)s) ORDER BY f.followers_count DESC".format(param2)
                res = query(sqlstmt, param={'date1': date1, 'date2': date2})
            else:
                sqlstmt = "select user_name, tweet_text from twitter_data where hashtag in ({})".format(param2)
        print(sqlstmt)
        res = query(sqlstmt)

    if uid is not None:
        param3 = ''
        for i in uid:
            param3 +='{}'.format(i) if param3 == '' else ',{}'.format(i)
        if date1 and date2 is not None:
            # select tweet_text from twitter_data where user_name='pensionarer' limit 10;
            sqlstmt = "select user_name, tweet_text from twitter_data where user_id in ('{}') and " \
                      "created_at between %(date1)s and %(date2)s)".format(param3)
            res = query(sqlstmt, param={'date1': date1, 'date2': date2})
        else:
            sqlstmt = "select user_name, tweet_text from twitter_data where user_id in ('{}')".format(param3)
            res = query(sqlstmt)
    return res


def search_solr(query_val, start_date='2016-01-01', end_date="2016-12-31", query_field=None):
    query_val = ' OR '.join(query_val)
    parameters = {}
    base_url = "http://localhost:8983/solr/sensemk/select?"
    date = parser.parse(start_date, dayfirst=True)
    sdate = date.isoformat() + 'Z'
    date = parser.parse(end_date)
    edate = date.isoformat() + 'Z'

    filter_param = 'created_at:[' + sdate + ' TO ' + edate + ']'
    parameters['fq'] = filter_param
    if query_field == None:
        parameters['q'] = query_val
    else:
        parameters['userName'] = query_val

    parameters['rows'] = '250000'
    parameters['fl'] = 'id,hashtags,tweet,user_id,userName,created_at'

    # print (parameters)
    # print (urllib.parse.urlencode(parameters))
    query_url = base_url + urllib.parse.urlencode(parameters)

    print (query_url)
    contents = getSolrResponse(query_url)
    return contents


def getSolrResponse(query_url):
    http = urllib3.PoolManager()
    response = http.request('GET', query_url)
    return eval(response.data)


def users_rank(users):
    pars = ''
    for u in users:
        pars = '{}'.format(u) if pars == '' else ',{}'.format(u)

    stmt = "select followers_count from followers_count_jsondata where user_id in ( " \
           "select user_id from twitter_data where hashtag in ('{}'))".format(pars)

    res = query(stmt)
    return [res[i][0] for i in range(len(res))]


def users_rank_with_detail(users):
    pars = ''
    for u in users:
        pars += '{}'.format(u) if pars == '' else ',{}'.format(u)

    stmt = "select user_id, screen_name, followers_count from followers_count_jsondata " \
           "where user_id in ({})".format(pars)
    # stmt = "select followers_count from followers_count_jsondata where user_id in ( " \
    #        "select user_id from twitter_data where hashtag in ('{}'))".format(pars)

    res = query(stmt)
    return sorted(res, key=lambda l: l[2])


# def users_rank(users):
#     pars = ''
#     for u in users:
#         pars += '{}'.format(u) if pars == '' else ',{}'.format(u)
#
#     stmt = "select rank from user_rank where user_id in ( select user_id from twitter_data where hashtag in ('{}'))".format(pars)
#
#     res = query(stmt)
#     return [res[i][0] for i in range(len(res))]


def read_tweets_for_prediction():
    path = './sensemaking/data/cascades/cascades_rt.txt'
    cascades = read_hashtags(path)
    return cascades


def read_hashtags(path=None):
    if path is None:
        path = './sensemaking/data/cascades/cascades.txt'
    cascades = {}
    with open(path) as f:
        for line in f:
            l = line.strip().split()
            if len(l[1:]) >= 3:
                ht = l[0]
                users = set()
                c = []
                for event in l[1:]:
                    e = event.split(',')
                    timestamp = float(e[0])
                    user = int(e[1])
                    users.add(user)
                    c.append([user, timestamp])

                cascades[ht] = sorted(c, key=lambda l: l[1])

    return cascades


def filter_cascades(cascades, obs_time_th, prd_time_th):
    filtered_cascades = {}
    for cas_id in cascades:
        c = cascades[cas_id]
        if len(c) > 10:
            first_inf_time = c[0][1]
            fifth_inf_time = c[5][1]
            tenth_inf_time = c[-1][1]
            obs_delta = abs(first_inf_time - fifth_inf_time)
            prd_delta = abs(first_inf_time - tenth_inf_time)
            if obs_delta <= (obs_time_th * 3600) and prd_delta <= (prd_time_th * 3600):
                filtered_cascades[cas_id] = c

    return filtered_cascades


def get_starters(cascade, obs_time):
    starters = [cascade[0][0]]
    for i in range(1, len(cascade)):
        delta = abs(cascade[i][1] - cascade[0][1])
        if delta < (obs_time * 3600):
            starters.append(cascade[i][0])

    return starters


def filter_cascades_deep(cascades, obs_time_th, prd_time_th, start_time):
    filtered_cascades = {}
    for cas_id in cascades:
        c = cascades[cas_id]
        new_c = []
        first_time_stamp = -1
        for i in range(0, len(c)):
            current_timestamp = c[i][1]
            if current_timestamp >= start_time:
                if first_time_stamp == -1:
                    first_time_stamp = c[i][1]
                    new_c.append(c[i])
                else:
                    delta = abs(c[i][1] - first_time_stamp)
                    if delta < (prd_time_th * 3600):
                        new_c.append(c[i])
                        if delta > (obs_time_th * 3600) and len(new_c) < 5:
                            break
                    else:
                        if len(new_c) > 10:
                            filtered_cascades[cas_id] = c[i:]
                            break
            #
            # if len(new_c) < 5:
            #     if delta < (obs_time_th * 3600):
            #         new_c.append(c[i])
            # else:
            #     if delta < (prd_time_th * 3600):
            #         new_c.append(c[i])
            #     else:
            #         if len(new_c) > 10:
            #             filtered_cascades[cas_id] = c
            #             break

    return filtered_cascades


def filter_starting_users(cascade, obs_time):
    first_inf_time = cascade[0][1]
    starting_users = {cascade[0][0]}
    for i in range(1, len(cascade)):
        current_inf_time = cascade[i][1]
        delta = abs(current_inf_time - first_inf_time)
        if delta < obs_time * 3600:
            starting_users.add(cascade[i][0])

    return starting_users


def virality_prediction_re_tweet_data(start_date, time_in_hour, threshold):
    """

    :param start_date: pass start date as string display greater than that date
    :param time_in_hour: less than the hour column copy_date
    :param threshold:
    :return:
    """
    params="'{}',{},{}".format(start_date, time_in_hour, threshold);
    
    sqlstmt="call virality_prediction({})".format(params)
    
    res = query(sqlstmt, param1='s')
    return res


def keyword_summary(search_text):
    res = search_solr(query_val=search_text)
    rec = []
    for obj in res['response']['docs']:
        hashtags = obj['hashtags'].split(',')
        for ht in hashtags:
            ts = obj['created_at'].split('T')[0]
            rec.append([obj['id'], ht, obj['user_id'], ts])

    rec_df = pd.DataFrame(rec, columns=['tweet_id', 'hashtag', 'user_id', 'created_at'])
    user_sum = rec_df.groupby('created_at')['user_id'].nunique().to_frame().reset_index()
    tweet_sum = rec_df.groupby('created_at')['tweet_id'].nunique().to_frame().reset_index()

    return user_sum.values.tolist(), tweet_sum.values.tolist()