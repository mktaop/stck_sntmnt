#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 20:25:58 2023

@author: avi_patel
"""


import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import streamlit as st

def get_sentiment_score(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)['compound']

def get_news_sentiment(stock_symbol):
    today = datetime.today().strftime('%m-%d-%Y')
    last_month = (datetime.today() - timedelta(days=30)).strftime('%m-%d-%Y')
    zlast_month = datetime.strptime(last_month, '%m-%d-%Y').date()
    url = f"https://finviz.com/quote.ashx?t={stock_symbol}&ty=c&ta=1&p=i15&b={last_month}&a={today}"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, features='html.parser')
    news_table = soup.find(id='news-table')
    news_df = pd.read_html(str(news_table))[0]
    news_df['Date'] = pd.to_datetime(news_df[0]).dt.round('H')
    news_df=news_df.loc[(news_df['Date'].dt.date >= zlast_month)]
    #news_df = news_df.drop(columns=['Time'])
    news_df['sentiment_score'] = news_df[1].apply(get_sentiment_score)
    news_df['sentiment'] = news_df['sentiment_score'].apply(lambda x: 'positive' if x > 0 else ('neutral' if x == 0 else 'negative'))
    #sentiment_by_hour = news_df.groupby('Date')['sentiment_score'].mean()
    #fig = px.line(sentiment_by_hour, x=sentiment_by_hour.index, y='sentiment_score')
    #fig.update_layout(title=f"Sentiment Analysis of {stock_symbol.upper()} News Headlines from Last 30 Days (Hourly)")
    #fig.show(renderer='browser')
    return news_df


#....page title, icon and layout set up and display
page_title="Headline Sentiment of a Publicly Traded Company (Last 30 days)"
page_icon=":chart_with_upwards_trend:"
layout="centered"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_icon + " " + page_title + " " + page_icon)
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
#....user input:  get a stock symbol....
stock_symbol = st.text_input('Stock symbol, please input and hit enter:  ')

#...once a symbol is entered and user presses return, create forecast and graph
if stock_symbol != '':
    
    df = get_news_sentiment(stock_symbol)
    sentiment_by_hour = df.groupby('Date')['sentiment_score'].mean()
    
    plt_title=f"Sentiment Analysis of {stock_symbol.upper()} News Headlines from Last 30 Days (Hourly)"
    fig=px.line(sentiment_by_hour, x=sentiment_by_hour.index, y='sentiment_score', title=plt_title, markers=True)
    
    
    st.write(fig)
    
else:
    pass

