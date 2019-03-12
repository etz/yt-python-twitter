#Installing: 
# 1. Add your own consumer key and access key data from Twitter Apps (https://developer.twitter.com/en/apps)
# 2. Add your own @handle in the handle variable. 
# 3. Change the search terms found in the twitter_bot.py file under "terms = []" in the findtweets() method
# 4. Install the Tweepy python module
# 5. Run twitter_bot.py
# YouTube Playlist: https://www.youtube.com/playlist?list=PLiaqnw9VgH2-C8-FStD6sf-YBKyWhPAHs

#!/usr/bin/python

import tweepy
import random
import time

#Do not Touch Lists
followed = []
friends = []
liked = []
time_start = time.time()
first_run = 0

# 1. Log onto twitter
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
handle = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

		
def findtweets():
	# 2. Find new tweets (under hashtags/search terms)
	terms = ["followback","youtube","f4f"]
	query = random.choice(terms)
	print("Selected term " + query)
	search = tweepy.Cursor(api.search, q=query, result_type="recent", lang="en").items(50) #Change the amount of tweets being searched for 50-75
	print("Searching under term...")
	# 3. Like new tweets (only if the user has more than 100 followers)
	for tweet in search:
		if (tweet.user.followers_count < 100 and tweet.user.statuses_count < 2500):
			print("Ignoring user " + tweet.user.screen_name)
			continue
		try:
			api.create_favorite(id=tweet.id)
			print("Following user " + tweet.user.screen_name)
			# 4. Follow the user, mute them.
			time.sleep(6)
			api.create_friendship(id=tweet.user.id)
			time.sleep(3)
			api.create_mute(id=tweet.user.id)
			# 5. Store their name, save it somewhere we can look back at it
			followed.append(tweet.user.id)
			liked.append(tweet.id)
		except tweepy.TweepError as e:
			if (e.args[0][0]['code'] == 139):	
				print ("Error with tweet " + str(tweet.id) + ", already liked!")
				liked.append(tweet.id)
				continue
			if (e.args[0][0]['code'] == 88):	
				print ("Rate limited..")
				time.sleep(60*15)
				continue
			print ("Error with tweet " + str(tweet.id))
def unfollow():
	print(" ~ Starting unfollow process ~ ")
	for user in followed:
		if (api.exists_friendship(screen_name=handle, id=user) == "false"):
			api.destroy_friendship(id=user)
			print("Unfollowed: " + user)
			followed.remove(user)
			continue
		# 7. Save the names of those who followed us back
		friends.append(user)
		print("Friended: " + user)
		followed.remove(user)
		

# 6. Unfollow users that don't follow back after 1 hour
def unlike():
	for tweet in liked:
		api.destory_favorite(id=tweet)
		print("Unliked: " + tweet)

# 8. Write the lists to a file in case of a error		
def write_to_file(filename, list):
	for item in list:
		filename.write(str(item) + "\n")	

# 9. Read from our files on first run.
if (first_run == 0):
	try:
		with open('followed_users.txt') as f:
			followed = f.read().splitlines()
		with open('liked_tweets.txt') as f:
			liked = f.read().splitlines()	
		with open('friend_users.txt') as f:
			friends = f.read().splitlines()	
	except:
		print("Files not found...waiting for first run.")
	first_run = 1

while (1 > 0):
	#Tweet Process
	if (time.time() > time_start+3600):
		unfollow()
	if (time.time() > time_start+(3600*3)):
		unlike()
	findtweets()
	
	#Logging
	print("Logging our files...")
	liked_tweets = open("liked_tweets.txt", "w")
	write_to_file(liked_tweets, liked)
	liked_tweets.close()
	followed_users = open("followed_users.txt", "w")
	write_to_file(followed_users, followed)
	followed_users.close()
	friend_users = open("friend_users.txt", "w")
	write_to_file(friend_users, friends)
	friend_users.close()
