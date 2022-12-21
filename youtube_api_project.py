# Import needed packages
from googleapiclient.discovery import build
import pandas as pd
from IPython.display import JSON
from dateutil.parser import parse

# Data viz packages
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker

# NLP
# !pip3 install wordcloud
# from wordcloud import WordCloud

# API INFO
api_key = 'AIzaSyCR1Wc4-GsgA4W_F3nCPDlRQDfzXw0Vxjg'
api_service_name = "youtube"
api_version = "v3"

# channel ID's
channel_ids = ['UCoOae5nYA7VqaXzerajD0lg',
               # more channels here 
]
# playlist ID
playlist_id = 'UUoOae5nYA7VqaXzerajD0lg'

# Get credentials and create an API client
youtube = build(api_service_name, api_version, developerKey = api_key)

def get_channel_stats(youtube, channel_ids):
    
    """
    Function: get_channel_stats
    ------
    
    Params:
    ------
    youtube: build object of Youtube API
    channel_ids: list of channel ID's

    Returns:
    ------
    dataframe with all channel stats for each channel

    """
    all_data = []
    
    request = youtube.channels().list(
        part = "snippet,contentDetails,statistics",
        id = ",".join(channel_ids)
    )

    response = request.execute()

    # loop through items
    for item in response['items']:
        data = {'channelName': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalViews': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        all_data.append(data)
    
    return pd.DataFrame(all_data)

def get_video_ids(youtube, playlist_id):

    """
    Function: get_video_ids
    ------

    Params:
    ------
    youtube: build object of Youtube API
    playlist_id: the ID of the playlist from Youtube

    Returns:
    ------
    List of all video_ids from channel

    """
    
    video_ids = []
    
    request = youtube.playlistItems().list(part = "snippet,contentDetails", playlistId=playlist_id,
                                          maxResults = 50)
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])
    
    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(part = "contentDetails", 
            playlistId = playlist_id,
            maxResults = 50,
            pageToken = next_page_token
        )
    
        response = request.execute()
        
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page_token = response.get('nextPageToken')
        
    return video_ids

def get_video_details(youtube, video_ids):

    """
    Function: get_video_details
    ------

    Params:
    ------
    youtube: build object of Youtube API
    video_ids: All of the video ID's from the channel

    Returns:
    ------
    Dataframe with columns: [
        video_id, 
        channelTitle, 
        title, 
        description, 
        tags, 
        publishedAt, 
        viewCount, 
        likeCount, 
        favouriteCount,
        commentCount,
        duration,
        definition,
        caption]
    with type of Object all

    """

    all_video_info = []
    
    for i in range(0, len(video_ids), 50):
        
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids[i:i + 50])
        )

        response = request.execute()

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }
            video_info = {}
            video_info['video_id'] = video['id']

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)

    return pd.DataFrame(all_video_info)

def get_comments_in_videos(youtube, video_ids):

    """
    Function: get_comments_in_videos
    ------

    Params:
    ------
    youtube: build object of Youtube API
    video_ids: All of the video ID's from the channel

    Returns:
    ------
    DataFrame with the top(last) comment from each video

    """

    all_comments = []
    for video_id in video_ids:
        try:
            
            request = youtube.commentThreads().list(
                part = 'snippet,replies',
                videoId = video_id
            )
            response = request.execute()

            comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items']]
            comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}

            all_comments.append(comments_in_video_info)
        except:
            continue
    
    return pd.DataFrame(all_comments)

def iso_duration_to_time(duration: str) -> str:

    """
    Function: iso_duration_to_time
    ------

    Params:
    ------
    duration: Youtube video duration which need to be converted to Seconds

    Returns:
    ------
    How many seconds is video

    """

    hours, minutes, seconds = 0, 0, 0
    if 'H' in duration:
        hours = int(duration.split('H')[0][2:])
    if 'M' in duration:
        minutes = int(duration.split('M')[0][-1:])
    if 'S' in duration:
        seconds = int(duration.split('S')[0][-1:])
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return total_seconds       
        


# Get the channel stats
channel_stats = get_channel_stats(youtube, channel_ids)

# Get video IDs
video_ids = get_video_ids(youtube, playlist_id)

# Create a DataFrame with the information about videos
video_df = get_video_details(youtube, video_ids)

# Create a DataFrame with comments from every video
comments_df = get_comments_in_videos(youtube, video_ids)



#Data pre-processing

print(video_df.isnull().any())
print(video_df.dtypes)

# From above we see that some columns need to be changed to numeric datatype
numeric_cols = ['viewCount', 'likeCount', 'favouriteCount', 'commentCount']
video_df[numeric_cols] = video_df[numeric_cols].apply(pd.to_numeric, axis = 1)

# Publish day in the week
video_df['publishedAt'] = video_df['publishedAt'].apply(lambda x: parse(x))
video_df['publishDayName'] = video_df['publishedAt'].apply(lambda x: x.strftime("%A"))

# Add new column with duration of video (in seconds)
video_df['durationSecs'] = video_df['duration'].apply(lambda x: iso_duration_to_time(x))

# Sample to show the result
print(video_df[['durationSecs', 'duration']])

# Add tag count
video_df['tagCount'] = video_df['tags'].apply(lambda x: 0 if x is None else len(x))


# Visualization


# Best performing videos
ax = sns.barplot(x = 'title', y = 'viewCount', data = video_df.sort_values('viewCount', ascending = False)[:9])
plot = ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x / 1000) + 'K'))

# Worst performing videos
ax = sns.barplot(x = 'title', y = 'viewCount', data = video_df.sort_values('viewCount', ascending = True)[:9])
plot = ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x / 1000) + 'K'))

# View distribution per video
sns.violinplot(video_df['channelTitle'], video_df['viewCount'])

# Views vs. Likes and Comments
fig, ax = plt.subplots(1, 2)
sns.scatterplot(data = video_df, x = 'commentCount', y = 'viewCount', ax = ax[0])
sns.scatterplot(data = video_df, x = 'likeCount', y = 'viewCount', ax = ax[1])

# Video duration
sns.histplot(data = video_df, x = 'durationSecs', bins = 50)

# Wordcloud for video titles
# Not worling, need to fix when I have free time

# import nltk
# nltk.download('stopwords')

# stop_words = set(stopwords.words('english'))
# video_df['title_no_stopwords'] = video_df['title'].apply(lambda x: [item for item in str(x).split() if item not in stop_words])

# all_words = list([a for b in video_df['title_no_stopwords'].tolist() for a in b])
# all_words_str = " ".join(all_words)

# def plot_cloud(wordcloud):
#     plt.figure(figsize = (30, 20))
#     plt.imshow(wordcloud)
#     plt.axis('off');

# wordcloud = WordCloud(width = 2000, height = 1000, random_state = 1, background_color = 'black',
#                      colormap = 'viridis', collocations = False).generate(all_words_str)

# plot_cloud(wordcloud)

# Upload schedule
day_df = pd.DataFrame(video_df['publishDayName'].value_counts())
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_df = day_df.reindex(weekdays)
ax = day_df.reset_index().plot.bar(x = 'index', y = 'publishDayName', rot = 0)