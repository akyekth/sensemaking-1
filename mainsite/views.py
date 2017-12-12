from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

from .sensemaking_io import *

import os
import time

import pandas as pd


class DashboardView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = {}

    def plot_selection_handle(self, request):
        """
        Handles when a user pick a hashtag from a plot

        :param request:
        :return:
        """
        path = './sensemaking/data/cascades/tweet_data.tsv'
        ht = [request.GET.get('hashtag', None)]
        ur = users_rank(ht)

        x, y = hashtag_summary_pandas(ht, path=path)
        # x, y = topk_monthly_hashtag_summary_tweet_distribution(ht)
        self.data = {'data': {'plot_selection': [[x, y]]}, 'rank': ur}

        return self.data

    def search_handle(self, request):
        """
        Handles when a user searches for one or more hashtags using the basic search
        :param request:
        :return:
        """
        search_text = request.GET.get('search_text', None).split(',')
        hashtag_coverage = percentage_per_hashtag(request.GET.get('search_text'))
        tweet_count = number_of_tweets_per_hashtag(request.GET.get('search_text'))
        user_count = number_of_users_per_hashtag(request.GET.get('search_text'))
        self.data['basic_stats'] = {}
        self.data['basic_stats']['hashtag_coverage'] = hashtag_coverage
        self.data['basic_stats']['tweet_count'] = tweet_count
        self.data['basic_stats']['user_count'] = user_count

        # text_res = tweet_text_input_based(ht=search_text)
        # text_res = search_solr(search_text)

        if len(search_text) == 1:
            ur = users_rank(search_text)
            res = hashtag_daily_summary(ht=[txt.strip() for txt in search_text])
            self.data['data'] = {'search': res, 'multiple': 0, 'rank': ur}
            return self.data
        elif len(search_text) > 1:
            ur = users_rank(search_text)
            res = hashtag_daily_summary(ht=[txt.strip() for txt in search_text])
            self.data['data'] = {'search': res, 'multiple': 1, 'rank': ur}
            return self.data
        return {}

    def advanced_search_handle(self, request):
        """
        Handles advanced search for hashtag, user or keyword.

        :param request:
        :return:
        """
        category = request.GET.get('category', None)

        search_text = request.GET.get('advanced_search_text', None).split(',')
        plot_type = request.GET.get('plot_type', None)
        search_text = [txt.strip() for txt in search_text]
        start = request.GET.get('from', None)
        end = request.GET.get('to', None)
        if category == 'hashtag':

            ur = users_rank(search_text)
            self.data = hashtag_daily_summary(search_text, start=start, end=end)
            response = {'data': self.data, 'rank': ur}
        elif category == 'user':

            ur = 0
            if plot_type == '0':
                path = './sensemaking/data/input/re_tweet_daily_sum.tsv'
                sep = '\t'
            elif plot_type == '1':
                path = './sensemaking/data/input/daily_user_hashtag_count.csv'
                sep = ','
            else:
                return {}
            self.data = user_daily_summary(path, search_text, start=start, end=end, sep=sep)
            response = {'data': self.data, 'rank': ur}
        else:
            user_sum, tweet_sum = keyword_summary(search_text)
            self.data['user_sum'] = user_sum
            self.data['tweet_sum'] = tweet_sum
            response = {'data': self.data}

        return response

    def init_load_handle(self):
        """
        Dashboard initial load handler

        :return:
        """
        # res = hashtag_monthly_summary()
        res = topk_monthly_hashtag_summary()
        tku = [int(u) for u in top_k_users(10)]
        users_data = top_k_users_retweet_dist(tku)
        self.data = {'data': {'init_render': [res, users_data]}}
        return self.data

    def get(self, request, *args, **kwargs):
        """
        Fired when a get request from the dashboard is sent
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if 'hashtag' in request.GET:
            hashtag_coverage = percentage_per_hashtag(request.GET.get('hashtag'))
            tweet_count = number_of_tweets_per_hashtag(request.GET.get('hashtag'))
            user_count = number_of_users_per_hashtag(request.GET.get('hashtag'))

            data = self.plot_selection_handle(request)
            data['basic_stats'] = {}
            data['basic_stats']['hashtag_coverage'] = hashtag_coverage
            data['basic_stats']['tweet_count'] = tweet_count
            data['basic_stats']['user_count'] = user_count
            return JsonResponse(data=data)
        elif 'search_text' in request.GET:
            data = self.search_handle(request)
            return JsonResponse(data=data)
        elif 'advanced_search_text' in request.GET:
            data = self.advanced_search_handle(request)
            return JsonResponse(data=data)
        elif 'search_for' in request.GET:
            search_for = request.GET.get('search_for').split(',')
            users_of_ht = int(request.GET.get('users_of_ht'))
            print('Users of ht', users_of_ht)
            if request.GET.get('grab') == 'hashtag':
                print('Searching for hashtags {}'.format(search_for))
                res = tweet_text_input_based(ht=search_for)
            else:
                print('Searching for users {}'.format(search_for))
                if users_of_ht == 1:
                    res = tweet_text_input_based(uname=search_for, users_of_ht=users_of_ht)
                else:
                    res = tweet_text_input_based(uname=search_for)
            print(res)
            data = {'data': res}
            return JsonResponse(data=data)

        else:
            data = self.init_load_handle()
            return render(request, 'mainsite/index.html', data)


class ViralityPredictionView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hashtag = ''
        self.threshold = 70
        self.obs_time = 1
        self.prd_time = 1
        self.hashtags = None
        self.cascades = {}

    def predict(self, request):
        """
        Handles when the predict event in the virality prediction page is clicked

        :param request:
        :return:
        """
        obs_time = int(request.GET.get('observation_time', None))
        prd_time = int(request.GET.get('prediction_time', None))
        threshold = int(request.GET.get('select_virality_threshold', None))
        target_ht = request.GET.get('select_hashtag', None)
        start_month = request.GET.get('start_month', None)
        start_day = request.GET.get('start_day', None)
        start_month = '0{}'.format(start_month) if len(start_month) == 1 else start_month
        start_day = '0{}'.format(start_day) if len(start_day) == 1 else start_day
        start_date = '2016-{}-{} 00:00:00'.format(start_month, start_day)
        start_timestamp = time.mktime(time.strptime(start_date, '%Y-%m-%d %H:%M:%S'))

        hts = read_hashtags()
        filtered_cascades = filter_cascades_deep(hts, obs_time, prd_time, start_timestamp)

        self.hashtags = list(set(filtered_cascades.keys()))
        mdl = load_model(obs_time, prd_time, threshold)
        target_cascade = hts[target_ht]
        emb = read_embedding()
        starters = get_starters(target_cascade, obs_time)
        starters_emb = emb.loc[starters]
        feature = [starters_emb.mean(axis=0).tolist()]

        prediction = mdl.predict_proba(feature)
        print("Prediction", prediction)
        users_rank = users_rank_with_detail(starters)
        label, confidence = prediction_detail(prediction[1][0])
        # data = {'hashtags': self.hashtags, 'ht': target_ht,
        #         'threshold': threshold, 'obs_time': obs_time,
        #         'prd_time': prd_time, 'confidence': confidence * 100,
        #         'predicted_label': label, 'upper_bound': 1000,
        #         'current_size': len(starters),
        #         'data': {'users_rank': users_rank}}
        data = {'data': {'hashtags': self.hashtags, 'ht': target_ht,
                         'threshold': threshold, 'obs_time': obs_time,
                         'prd_time': prd_time, 'confidence': confidence * 100,
                         'predicted_label': label, 'upper_bound': 1000,
                         'current_size': len(starters),
                         'users_rank': users_rank}}
        return data

    def filter_cascades(self, request):
        """
        Filters as the user selects different prediction time on the GUI
        :param request:
        :return:
        """
        obs_time = int(request.GET.get('observation_time', None))
        prd_time = int(request.GET.get('prediction_time', None))
        # valid_data = hashtags_in_window(path=path, obs_time=obs_time, prd_time=prd_time)
        # self.hashtags = list(set(valid_data.hashtag))
        ht_cascades = read_hashtags()
        start_month = request.GET.get('start_month', None)
        start_day = request.GET.get('start_day', None)
        start_month = '0{}'.format(start_month) if len(start_month) == 1 else start_month
        start_day = '0{}'.format(start_day) if len(start_day) == 1 else start_day
        start_date = '2016-{}-{} 00:00:00'.format(start_month, start_day)
        start_timestamp = time.mktime(time.strptime(start_date, '%Y-%m-%d %H:%M:%S'))
        print("Timestamp ", start_timestamp)
        filtered_cascades = filter_cascades_deep(ht_cascades, obs_time, prd_time, start_timestamp)
        self.hashtags = list(set(filtered_cascades.keys()))
        data = {'data': {'hashtags': self.hashtags, 'prd_div': 'collapse in'}}
        return data

    def init_model_args(self, data):
        self.hashtag = data.get('select_hashtag')
        self.threshold = int(data.get('select_virality_threshold'))
        self.obs_time = int(data.get('observation_time'))
        self.prd_time = int(data.get('prediction_time'))

    def get(self, request, *args, **kwargs):

        if 'prediction_time' in request.GET and 'predict' not in request.GET:
            return JsonResponse(self.filter_cascades(request))
        elif 'predict' in request.GET:
            return JsonResponse(self.predict(request))
        else:
            data = {'data': {'hashtags': [], 'prd_div': 'collapse in'}}
            return render(request, 'mainsite/charts.html', data)
