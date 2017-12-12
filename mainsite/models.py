# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ComMembership(models.Model):
    id_str = models.ForeignKey('Users', models.DO_NOTHING, db_column='id_str', blank=True, null=True)
    community = models.ForeignKey('Community', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'com_membership'


class Community(models.Model):
    community_id = models.BigIntegerField(primary_key=True)
    size = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'community'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Dummy(models.Model):
    text = models.CharField(max_length=100, blank=True, null=True)
    f_usage = models.DateTimeField(blank=True, null=True)
    l_usage = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dummy'


class Dummy2(models.Model):
    t1 = models.BigIntegerField(blank=True, null=True)
    t2 = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dummy2'
        unique_together = (('t1', 't2'),)


class Followee(models.Model):
    id_str = models.ForeignKey('Users', models.DO_NOTHING, db_column='id_str', blank=True, null=True)
    followee_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'followee'


class Followers(models.Model):
    id_str = models.ForeignKey('Users', models.DO_NOTHING, db_column='id_str', blank=True, null=True)
    followersid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'followers'


class Genderequality(models.Model):
    s_no = models.AutoField(primary_key=True)
    hashtag = models.CharField(max_length=25, blank=True, null=True)
    no_of_tweets = models.BigIntegerField(blank=True, null=True)
    total_tweets_period = models.BigIntegerField(blank=True, null=True)
    ratio = models.FloatField(blank=True, null=True)
    min_date = models.DateTimeField(blank=True, null=True)
    max_date = models.DateTimeField(blank=True, null=True)
    no_of_retweet = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genderequality'


class Hashtag(models.Model):
    hashtag_id = models.BigAutoField(primary_key=True)
    text = models.TextField(unique=True, blank=True, null=True)
    first_usage = models.DateTimeField(blank=True, null=True)
    last_usage = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hashtag'


class Help(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    uid = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    uname = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'help'


class Mentions(models.Model):
    tweet = models.ForeignKey('Tweet', models.DO_NOTHING, blank=True, null=True)
    user_id_str = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_id_str', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mentions'


class MentionsParty(models.Model):
    tweet = models.ForeignKey('Tweet', models.DO_NOTHING, blank=True, null=True)
    party_name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mentions_party'


class RelatedHashtag(models.Model):
    keyword = models.CharField(max_length=100, blank=True, null=True)
    hashtag = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'related_hashtag'


class RelatedTerms(models.Model):
    keyword = models.CharField(max_length=100, blank=True, null=True)
    term = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'related_terms'


class Retweet(models.Model):
    tweet_id_new = models.ForeignKey('Tweet', models.DO_NOTHING, db_column='tweet_id_new', blank=True, null=True)
    tweet_id_old = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'retweet'


class T(models.Model):
    tw = models.BigIntegerField(blank=True, null=True)
    li = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't'


class Tweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    id_str = models.BigIntegerField(blank=True, null=True)
    retweet_count = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    in_reply_to_user_id = models.BigIntegerField(blank=True, null=True)
    in_reply_to_status_id = models.BigIntegerField(blank=True, null=True)
    d = models.IntegerField(blank=True, null=True)
    m = models.IntegerField(blank=True, null=True)
    w = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tweet'


class TweetsHashtag(models.Model):
    tweet = models.ForeignKey(Tweet, models.DO_NOTHING, blank=True, null=True)
    hash = models.ForeignKey(Hashtag, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tweets_hashtag'
        unique_together = (('tweet', 'hash'),)


class Urls(models.Model):
    tweet = models.ForeignKey(Tweet, models.DO_NOTHING, blank=True, null=True)
    url = models.CharField(max_length=2083, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'urls'


class Users(models.Model):
    id_str = models.BigIntegerField(primary_key=True)
    verified = models.IntegerField(blank=True, null=True)
    followers_count = models.BigIntegerField(blank=True, null=True)
    id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    friends_count = models.BigIntegerField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
