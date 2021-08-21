import string
import re
import nltk

nltk.download("twitter_samples")
nltk.download("stopwords")
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords, twitter_samples

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

tweet_tokenizer = TweetTokenizer(
    preserve_case=False, strip_handles=True, reduce_len=True
)

# Stop words are messy and not that compelling;
# "very" and "not" are considered stop words, but they are obviously expressing sentiment

# The porter stemmer lemmatizes "was" to "wa".  Seriously???

# I'm not sure we want to get into stop words
stopwords_english = stopwords.words("english")

# Also have my doubts about stemming...
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()


def process_tweet(tweet):
    """
    Input:
        tweet: a string containing a tweet
    Output:
        tweets_clean: a list of words containing the processed tweet

    """
    # remove stock market tickers like $GE
    tweet = re.sub(r"\$\w*", "", tweet)
    # remove old style retweet text "RT"
    tweet = re.sub(r"^RT[\s]+", "", tweet)
    # remove hyperlinks
    tweet = re.sub(r"https?:\/\/.*[\r\n]*", "", tweet)
    # remove hashtags
    # only removing the hash # sign from the word
    tweet = re.sub(r"#", "", tweet)
    # tokenize tweets
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    tweet_tokens = tokenizer.tokenize(tweet)
    ### START CODE HERE ###
    tweets_clean = []
    for word in tweet_tokens:
        if (
            word not in stopwords_english
            and word not in string.punctuation  # remove stopwords
        ):  # remove punctuation
            # tweets_clean.append(word)
            stem_word = stemmer.stem(word)  # stemming word
            tweets_clean.append(stem_word)
    ### END CODE HERE ###
    return tweets_clean


# let's not reuse variables
# all_positive_tweets = twitter_samples.strings('positive_tweets.json')
# all_negative_tweets = twitter_samples.strings('negative_tweets.json')


def load_tweets():
    all_positive_tweets = twitter_samples.strings("positive_tweets.json")
    all_negative_tweets = twitter_samples.strings("negative_tweets.json")
    return all_positive_tweets, all_negative_tweets


# Layers have weights and a foward function.
# They create weights when layer.initialize is called and use them.
# remove this or make it optional


class Layer(object):
    """Base class for layers."""

    def __init__(self):
        self.weights = None

    def forward(self, x):
        raise NotImplementedError

    def init_weights_and_state(self, input_signature, random_key):
        pass

    def init(self, input_signature, random_key):
        self.init_weights_and_state(input_signature, random_key)
        return self.weights

    def __call__(self, x):
        return self.forward(x)


def get_batch(source, i):
    """
    returns a batch
    """
    bptt = 35
    seq_len = min(bptt, len(source) - 1 - i)
    data = source[i : i + seq_len]
    target = source[i + 1 : i + 1 + seq_len].view(-1)

    return data, target


def batchify(data, bsz):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).t().contiguous()
    return data


# to detach the hidden state from the graph.
def detach(hidden):
    """
    This function detaches every single tensor.
    """
    if isinstance(hidden, torch.Tensor):
        return hidden.detach()
    else:
        return tuple(detach(v) for v in hidden)
