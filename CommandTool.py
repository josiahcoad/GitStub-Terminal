user_lang = ["SQL", "Java", "JavaScript", "C#", "C++", "Python", "Ruby on Rails"]

'''^^^-------------Edit Prefered languages!------------^^^'''
#!/usr/bin/python3
import requests
import json
import os
import sys

class InputError(Exception):
	pass

def printf(obj):
	try:
		print (json.dumps(obj, sort_keys=True,
		                  indent=4, separators=(',', ': ')))
	except:
		print("Can't parse! (Must not be a json obj)")

def _get(url):
	token = "3685ef1db2f007427ff57f5b93daa3c41f67fd35"
	return requests.get(url, headers={'Authorization': "token " + token}).json()

def get_contribs(repo):
	try:
		contribs = _get(repo)
		assert contribs[0].get("message") != "Not Found"
		return contribs
	except:
		print ("Not a found username/reponame. Please try again")
	

def get_repos(user):
	username = user["login"]
	repos = _get("https://api.github.com/users/" + username + "/repos")
	return repos

def score(repo):
	try:
		tot = 0
		tot += repo["forks_count"] * 3
		tot += repo["watchers_count"] * 4
		tot += repo["stargazers_count"] * 5
		return tot
	except:
		print("Error found when finding related finds. Please try some other repo.")

def language_overlap(repo_lang, user_lang):
	return repo_lang in user_lang
	# in_repo = _get(repo["languages_url"]).keys()
	# return list(set(user_lang).intersection(in_repo))

def print_top(best_repos, num):
	# make sure theres enough results to return, else return whatever there is
	if len(best_repos) < num:
		num = len(best_repos)
	# finally, print out to console
	os.system("clear")
	print("__Your Recomended Repos__")
	i = 0
	while (i < num):
		repo = best_repos[i]
		print(" ")
		print("[" + str(i) + "] " + repo["name"])
		print("|> by " + repo["owner"]["login"])
		print("|> Popularity Index: " + str(repo["tot_score"]))
		print("|> Primary Language: " + repo["language"])
		i += 1


def get_recomend_repo(repo_name):
	limit = _get("https://api.github.com/rate_limit")["resources"]["core"] # <----
	if limit["remaining"] == 0: raise Exception("Not enough requests to do it. Try again later.")
	# print ("Your remaining Queries for the hour: " + str(limit["remaining"]))
	source_repo = "https://api.github.com/repos/" + repo_name + "/contributors"	
	contribs = get_contribs(source_repo)
	best_repos = []
	print ("Thinking really hard so you dont have to...")
	for contrib in contribs:
		# get the other repos of contributer
		contrib_repos = get_repos(contrib)

		# get repos with most forks
		contrib_topscore = 0
		good_repo = False

		for contrib_repo in contrib_repos:
			good_repo = contrib_repo["language"] in user_lang
			if good_repo:
				if score(contrib_repo) >= contrib_topscore:
					contrib_topscore = score(contrib_repo)
					contrib_best = contrib_repo
		if good_repo:
			contrib_best["tot_score"] = contrib_topscore
			best_repos.append(contrib_best)
	
	# sort list based on score
	best_repos = sorted(best_repos, key=lambda repo: repo["tot_score"], reverse=True)
	return best_repos


def print_issues(repo):
	issues = _get(repo["issues_url"][:-9])
	if len(issues) == 0:
		print("No issues") 
	else:
		for iss in issues:
			if iss["state"] == "open":
				print (iss["title"])
				print ("--> " + iss["url"])
				print ("\n(if on a mac, cmnd+click to open link)")

	option = input("Press x to exit; o to continue >> ")
	return option


# if len(sys.argv) != 3: ValueError("Incorrect Command Line Args.")
while True:
	if len(sys.argv) == 2:
		repo_name = sys.argv[1] # hmmmm
	else:
		repo_name = input("Enter a 'username/repository' that you like: ")
	if len(repo_name.split("/")) == 2: break
	else: print ("Incorrect Entry. Try Again.")

num_results = 5
top_repos = get_recomend_repo(repo_name)

print_top(top_repos, 5)


while True:
	interested = int(input("\nEnter repo # >> "))
	# print_top(list(top_repos[interested]), num_results)
	print ("\nCool! So for " + top_repos[interested]["name"].title())
	option = input("Enter 'c' to open the project, 'i' to look at issues >> ")
	if option == 'c':
		url = top_repos[interested]["clone_url"]
		os.system("echo 'git clone %s' | pbcopy" % url)
		print("Git clone url clipboard just for you ;)")
		os.system("open " + url)
	elif option == 'i':
		os.system("clear")
		print("______ Issues ______")
		opt = print_issues(top_repos[interested])
		if opt == "o":
			print_top(top_repos, num_results)
		elif opt == "x": break
	elif option == 'x': break
	else:
		print ("ohh. What did you do? I said 'i', 'c', 'x' or 'o'!")

print("Have Fun!")
