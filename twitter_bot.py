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
delay_between_search = 30

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def findtweets():
	# Find 'new' tweets (under hashtags/search terms)
	terms = ["twitch","youtube","follow"]
	query = random.choice(terms)
	search = tweepy.Cursor(api.search, q=query, result_type="recent", lang="en").items(50) #Change the amount of tweets being searched for 50-75
	print("Searching under term..." + query)
	# Like 'new' tweets (only if the user has more than 100 followers & less than 2500 tweets)
	for tweet in search:
		if (tweet.user.followers_count < 100 and tweet.user.statuses_count < 2500):
			print("Ignoring user " + tweet.user.screen_name)
			continue
		try:
			api.create_favorite(id=tweet.id)
			print("Following user " + tweet.user.screen_name)
			# Follow the user, and then mute them.
			time.sleep(6)
			api.create_friendship(id=tweet.user.id)
			time.sleep(3)
			api.create_mute(id=tweet.user.id)
			# Store their name in a file to be reviewed later.
			followed.append(tweet.user.id)
			liked.append(tweet.id)
		except tweepy.TweepError as e:
			#Catching errors
			if (e.args[0][0]['code'] == 139):
				print ("Error with tweet " + str(tweet.id) + ", already liked!")
				liked.append(tweet.id)
				continue
			if (e.args[0][0]['code'] == 88):
				print ("Rate limited..")
				time.sleep(60*15)
				continue
			print ("Error with tweet " + str(tweet.id))

# Unfollow() provides a method for unfollowing users that have not followed you back. Unfollow() also
# adds users that have followed you back to your "friends" list to be unfollowed at a later time.
def unfollow():
	print(" ~ Starting unfollow process ~ ")
	for user in followed:
		status = api.show_friendship(source_screen_name=handle, target_id=user)
		# If the user is not following me back:
		if (str(status[1].following) == "False"):
			try:
				# Unfollow them
				api.destroy_friendship(id=user)
				print("Unfollowed: " + str(user))
				followed.remove(user)
				continue
			except:
				print("Could not Unfollow: " + str(user))
		# Save the names of those who followed us back.
		friends.append(user)
		print("Friended: " + str(user))
		followed.remove(user)

# Unfollow_friends(): Unfollows users that DO follow you back.
def unfollow_friends():
	print(" ~ Starting unfollow_friends process ~ ")
	for user in friends:
		try:
			api.destroy_friendship(id=user)
			print("Unfollowed: " + str(user))
			friends.remove(user)
		except:
			print("Could not Unfollow: " + str(user))

# Unlike statuses liked with the bot
def unlike():
	for tweet in liked:
		try:
			api.destroy_favorite(id=tweet)
			print("Unliked: " + str(tweet))
			liked.remove(tweet)
		except tweepy.TweepError as e:
			if(e.args[0][0]['code'] == 144):
				print("This status no longer exists... removing..")
				liked.remove(tweet)
				continue
			print("An unknown error occured")

# Write our actions to separate files in case of a error
def write_to_file(filename, list):
	for item in list:
		filename.write(str(item) + "\n")

# 9. Read from our files on first run.
if (first_run == 0):
	try:
		with open('followed_users.txt') as f:
			followed = f.read().splitlines()
			if (len(followed) > 100):
				unfollow()
		with open('liked_tweets.txt') as f:
			liked = f.read().splitlines()
			if (len(liked) > 100):
				unlike()
		with open('friend_users.txt') as f:
			friends = f.read().splitlines()
			if (len(friends) > 100):
				unfollow_friends()
	except:
		print("Files not found...waiting for first run.")
	first_run = 1

while (1 > 0):
	since_launch = int(time.time() - time_start)

	print ("Running Twitter Bot... " + str(since_launch) + " seconds since launch")

	# Tweeting 
	if (time.time() > time_start+(3600*3)):
		time_start = time.time()
		unfollow_friends()
	if (time.time() > time_start+3600 and len(followed) > 100):
		unfollow()
		unlike()
	if (time.time() > time_start+180):
		print(str(since_launch/60) + " minutes since launch, running additional commands in " + str(60-(since_launch/60)) + " minutes")

	findtweets()
	time.sleep(delay_between_search)

	# Logging
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
