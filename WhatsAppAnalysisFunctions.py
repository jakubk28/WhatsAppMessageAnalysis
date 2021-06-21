import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

def import_messages(messages_path):
    '''
    
    Parameters
    ----------
    messages_path : .txt file, raw file obtained from WhatsApp

    Returns
    -------
    raw_messages : DataFrame
        tidied version of WhatsApp messages that were entered, in a clean format that is ready for analysis.

    '''
    
    raw_messages = pd.read_csv((messages_path),sep='[',header=None,error_bad_lines=False,warn_bad_lines=False)
    raw_messages.columns=['NaNs','text']
    raw_messages = raw_messages.drop(columns=['NaNs'])
    raw_messages = raw_messages.dropna()
    raw_messages = raw_messages[~raw_messages['text'].str.contains('omitted')]
    #extract date,time, and text from each single line from raw .txt file entered
    raw_messages['date'] = raw_messages['text'].str[0:10]
    raw_messages['time'] = raw_messages['text'].str[12:20]
    raw_messages['text'] = raw_messages['text'].str[22:]
    raw_messages[['name', 'message']] = raw_messages['text'].str.split(":",n=1, expand=True)
    raw_messages = raw_messages.drop('text',axis=1)
    #change order of columns to have name first, followed by date time and finally text
    raw_messages = raw_messages[['name','date','time','message']]
    print('Finished importing messages')
    return raw_messages



def basic_stats(clean_messages):
    '''

    Parameters
    ----------
    clean_messages : Output of function 'import_messages' , dataframe object

    Returns
    -------
    Print out of informative statistics

    '''
    
    print('------------------------------------------------------')
    print('Basic stats')
    print('------------------------------------------------------')
    
    number_of_days = clean_messages.groupby('date').size().size
    print('Number of days talking: ', number_of_days)
    
    print('------------------------------------------------------')
    
    #total number of messages sent by each person
    total_messages = clean_messages.groupby('name').count().drop(columns=['date','time'])
    total = total_messages.iloc[0,0] + total_messages.iloc[1,0]
    user1 = total_messages.iloc[0,0]
    user2 = total_messages.iloc[1,0]
    
    print('Total number of messages sent: ',total, '(',round(total/number_of_days,2),'/day)')
    print('Sent by',total_messages.index[0],':',user1,'(',round(user1/number_of_days,2),'/day)',',  (',round(user1/total*100,2),'% )')
    print('Sent by',total_messages.index[1],':',user2,'(',round(user2/number_of_days,2),'/day)',',  (',round(user2/total*100,2),'% )')

    print('------------------------------------------------------')
    
    #calculating average number of texts per user before response
    messages_per_person = clean_messages['name']
    from itertools import groupby
    sender_list = messages_per_person.values.tolist()
    count_dups = [sum(1 for _ in group) for _, group in groupby(sender_list)]
    #count even and odd number of messages until the next reply
    user1 = count_dups[::2]
    user2 = count_dups[1::2]
    print('Average number of messages sent by person berfore response:')
    print(clean_messages.iloc[0,0], ':', round(np.mean(user1),2))
    if clean_messages.iloc[0,0] != total_messages.index[0]:
        other_user = total_messages.index[0] 
    else:
        other_user = total_messages.index[1] 
    print(other_user, ':', round(np.mean(user2),2))
    print('------------------------------------------------------')


def total_messages_plot(clean_messages,rolling_average_period):
    '''

    Parameters
    ----------
    clean_messages : Dataframe
        Output from import_messages().
    rolling_average_period : Int
        Number of days that the rolling average will be calculated, set to 1 for rolling average to not be
        calculated.

    Returns 
    -------
    Rolling average plot of number of messages sent over period of time

    '''    
    daily_sums = clean_messages.groupby(['date','name']).size().reset_index()
    daily_sums.columns = ['date','name','sent_messages']
    ds = daily_sums.pivot(index='date',columns='name',values='sent_messages')
    ds['datetime'] = ds.index
    ds.index = pd.to_datetime(ds.index)
    #create rolling average with window period being an input to function
    ds2 = ds.resample("1d").sum().fillna(0).rolling(window=rolling_average_period, min_periods=1).mean()
    
    #plot result
    plt.figure(figsize=(20,7))
    ds2.iloc[:,0].plot(color='blue', grid=True,alpha=0.6)
    ds2.iloc[:,1].plot(color='red', grid=True,alpha=0.6)
    plt.legend(loc=2)
    plt.xlabel('Date')
    plt.ylabel('Number of messages sent')
    plt.title('%i day rolling average of messages sent' %rolling_average_period)
    plt.show()
    
def day_hour_plot(clean_messages):
    '''

    Parameters
    ----------
    clean_messages : Output of function 'import_messages' , dataframe object

    Returns
    -------
    Visual of what day messages are sent on the most

    '''
    #trim to just the hour, rather than minutes and seconds
    clean_messages['hour'] = clean_messages['time'].str[0:2]
    #trying to group by time to see what time we chat the most
    time_sums = clean_messages.groupby(['hour']).size().reset_index()
    time_sums.columns = ['Hour','Total messages sent']
    
    ##WHAT DAY ARE MESSAGES SENT MOST ON? PLOT
    clean_messages['weekday'] = pd.to_datetime(clean_messages['date']).dt.day_name()
    weekday_sums = clean_messages.groupby(['weekday']).size().reset_index()
    weekday_sums.columns = ['Weekday','Total messages sent']
    
    fig, (ax1, ax2) = plt.subplots(1, 2,figsize=(17,7))
    ax1.bar(time_sums['Hour'], time_sums['Total messages sent'])
    ax1.set_xlabel('Hour')
    ax1.set_ylabel('Total messages sent')
    ax2.bar(weekday_sums['Weekday'], weekday_sums['Total messages sent'])
    ax2.set_xlabel('Weekday')
    ax2.set_ylabel('Total messages sent')


def plot_wordcloud(clean_messages,nwords):
    '''

    Parameters
    ----------
    clean_messages : Output of function 'import_messages' , dataframe object

    nwords : Int
        How many top words from messages to include in word cloud.

    Returns
    -------
    Word cloud plot of most commonly used words after exlucding stopwords.

    '''
    #extract only name and text, as time and date are not important
    text_and_sender = clean_messages[['name','message']]
    #new column for tokenized words
    text_and_sender['tokenized_sents'] = text_and_sender.apply(lambda row: nltk.word_tokenize(row['message']), axis=1)
    #number of tokens per message
    text_and_sender['sents_length'] = text_and_sender.apply(lambda row: len(row['tokenized_sents']), axis=1)
    #average words sent per user
    average_words_per_user = text_and_sender.groupby('name').mean()
    
    print('Average number of words per message by ',average_words_per_user.index[0],':',round(average_words_per_user.iloc[0,0],2))
    print('Average number of words per message by ',average_words_per_user.index[1],':',round(average_words_per_user.iloc[1,0],2))
    
    text_and_sender['message'] = text_and_sender['message'].str.lower()
    text_and_sender['message'] = text_and_sender['message'].str.replace('[^\w\s]','')
    stop = stopwords.words('english')
    #added extra stop words, mostly shortenings without apostrohpe that were not included
    stop.extend(['itll',
                 'its',
                 'ill',
                 'well',
                 'ive',
                 'im',
                 'id',
                 'cant',
                 'dont',
                 'thats',
                 'gonna',
                 'thatd',
                 'theyre',
                 'like',
                 'couldnt',
                 'wont',
                 'yeah',
                 'ye',
                 'want',
                 'still',
                 'okay',
                 'got',
                 'shes',
                 'tho',
                 'didnt',
                 'youre',
                 'hes',
                 'put',
                 'bit',
                 'youll',
                 'doesnt',
                 'havent',
                 'theres'])
    #remove words that are in stopwords from tokens
    text_and_sender['messages_clean'] = text_and_sender['message'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    text_and_sender['messages_clean'].replace('', np.nan, inplace=True)
    text_and_sender.dropna(subset=['messages_clean'], inplace=True)
    #tokenize clean messages, changing sentences to singular words
    text_and_sender['tokens'] = text_and_sender["messages_clean"].apply(nltk.word_tokenize)
    tokenized_messages = text_and_sender[['name','tokens']]
    #change from word1,word2,word3 format seperated by commas to actually rows of words
    tokenized_messages2 = tokenized_messages.explode('tokens')
    text = tokenized_messages2['tokens']
    #how many top words to include
    top_n_words = text.value_counts()[:nwords]
    top_n_words = top_n_words.reset_index()
    #create dictionary object that can be used by word cloud package to create wordcloud, in the form, word:number of appearances
    data = dict(zip(top_n_words['index'].tolist(), top_n_words['tokens'].tolist()))
    #generate wordcloud
    wordcloud = WordCloud(max_words=100,colormap='tab20c',relative_scaling=1,prefer_horizontal=0.95,width=3000, height=3000).generate_from_frequencies(data)
    plt.figure(figsize=[12, 12])
    plt.imshow(wordcloud,interpolation="bilinear")
    plt.axis("off")
    plt.show()
    

clean_messages = import_messages('C:/Users/Jakub/Desktop/_chat.txt')
basic_stats(clean_messages)
total_messages_plot(clean_messages,7)
day_hour_plot(clean_messages)
plot_wordcloud(clean_messages,50)
