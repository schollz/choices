from flask import Flask, render_template, redirect
import json
from datetime import datetime
import time
import os
import random
from collections import OrderedDict
import feedparser
import re
from operator import itemgetter

def getScienceFeed():
	articles = []
	state = json.load(open('data/state.json','r'),object_pairs_hook=OrderedDict)
	if 'science_feed' not in state or state['science_feed']['last_updated'] ==  int(time.time()/(60*60*24)):
		# Science Magazine
		d = feedparser.parse('http://www.sciencemag.org/rss/current.xml')
		for entry in d['entries']:
			if "Report" in entry['title'] or "Research Article" in entry['title']:
				article = {}
				article['title'] = entry['title'].split(']')[1].strip()
				article['summary'] = entry['summary'].split('Authors:')[0].strip()
				article['link'] = 'http://dx.doi.org/' + entry['dc_identifier']
				article['date'] = entry['updated']
				article['section'] = entry['title'].split(']')[0].strip()[1:]
				article['journal'] = 'Science'
				articles.append(article)

		# Nature 
		d = feedparser.parse('http://feeds.nature.com/nature/rss/current')
		for entry in d['entries']:
			if "Article" == entry['prism_section'] or "Review" == entry['prism_section'] or "Letter" == entry['prism_section']:
				article = {}
				article['title'] = entry['title']
				article['summary'] =entry['summary']
				article['link'] = 'http://dx.doi.org/' +  entry['dc_identifier'].split('doi:')[1]
				article['date'] = entry['updated']
				article['section'] = entry['prism_section']
				article['journal'] = 'Nature'
				articles.append(article)

		# Nature communications
		d = feedparser.parse('http://feeds.nature.com/ncomms/rss/current')
		for entry in d['entries']:
			if "Corrigendum" not in entry['title']:
				article = {}
				article['title'] = entry['title']
				article['summary'] = entry['summary']
				article['link'] = 'http://dx.doi.org/' + entry['dc_identifier'].split('doi:')[1]
				article['date'] = entry['updated']
				article['section'] = 'Nature Communications'
				article['journal'] = 'Nature Communications'
				articles.append(article)
		
		# PNAS
		d = feedparser.parse('http://www.pnas.org/rss/current.xml')
		for entry in d['entries']:
			if "Corrections" not in entry['prism_section'] and  "QnAs" not in entry['prism_section'] and "Commentaries" not in entry['prism_section'] and "Letters" not in entry['prism_section'] and "Opinion" not in entry['prism_section'] and "This Week" not in entry['prism_section']:
				article = {}
				article['title'] = entry['title'].split('[')[0]
				article['summary'] = entry['summary']
				article['link'] = entry['link'].split('.short')[0]
				article['date'] = entry['updated'].split('T')[0]
				article['section'] = entry['prism_section']
				article['journal'] = 'PNAS'
				articles.append(article)
		
		# JBC
		d = feedparser.parse('http://feeds.feedburner.com/JBC_ProteinStructureAndFolding')
		for entry in d['entries']:
			article = {}
			article['title'] = entry['title'].split('[')[0]
			article['summary'] = entry['summary'].split('<img')[0]
			article['link'] = entry['id'].split('.short')[0]
			article['date'] = entry['updated'].split('T')[0]
			article['section'] = entry['title'].split(']')[0].strip()[1:]
			article['journal'] = 'JBC'
			articles.append(article)
				
		articles_filtered = []
		
		# Filter these words out
		summary_filter_words = ['galaxies','galaxy','supernova','immunological','transplant','microrna','leuko','histone','cytoskeleton','spin ','pet','transcription factor','hiv-1','microwave','superconductor','crystallographic','spin-','monolayer','sox9','cd1','cryo-em','glycoprotein','kinase','cancer','insulin','GPCR']
		title_filter_words = ['ocean','laser','microwave','clinical','quantum','microrna','leuko','histone','cytoskeleton','spin ','pet','transcription factor','hiv-1','superconductor','crystallographic','spin-','monolayer','sox9','cd1','cryo-em','membrane','pump','toxicity','kinase','tau','allosteric','integrin','hepatitis','assembly','epitope','cancer','GPCR']
		
		# Highlight articles with these words
		important_words = []
		super_important_words = ['afm','folding','single-molecule','single molecule']
		
		for article in articles:
			passes_filter = True
			need_to_read = False
			super_important = False
			for word in summary_filter_words:
				if word in article['summary'].lower():
					passes_filter = False
			for word in title_filter_words:
				if word in article['title'].lower():
					passes_filter = False
			for word in important_words:
				if word in article['summary'].lower() or word in article['title'].lower():
					need_to_read = True
			for word in super_important_words:
				if word in article['summary'].lower() or word in article['title'].lower():
					super_important = True
			if passes_filter or need_to_read or super_important:
				article['need_to_read'] = need_to_read
				article['super_important'] = super_important
				if not (super_important or need_to_read):
					article['summary'] = ' '.join(re.split(r'(?<=[.:;])\s', article['summary'])[:2])
				articles_filtered.append(article)
			
		state['science_feed'] = {}	
		state['science_feed']['last_updated'] = int(time.time()/(60*60*24))
		state['science_feed']['feed'] = articles_filtered
		json.dump(state,open('data/state.json','w'),indent=4, separators=(',', ': '))
		
	newlist = sorted(state['science_feed']['feed'], key=itemgetter('date'), reverse=True)
	return newlist
	
def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
      if random.randrange(num + 2): continue
      line = aline
    return line

def generate_navigation(path):
	day_of_week = datetime.now().strftime('%A').lower()
	day_of_month = str(int(datetime.now().strftime('%d')))

	state = OrderedDict()
	if not os.path.exists('data'):
		os.makedirs('data')
	
	if not os.path.isfile('data/state.json'):
		bookmarks = OrderedDict()
		bookmarks = json.load(open('config.json','r'),object_pairs_hook=OrderedDict)

		for category in bookmarks:
			for page in bookmarks[category]:
				
				# check if everything has time stamp
				if "last_checked" not in bookmarks[category][page]:
					bookmarks[category][page]['last_checked'] = int(time.time()/(60*60*24))
					json.dump(bookmarks,open('data/bookmarks.json','w'),indent=4, separators=(',', ': '))
				
				if "checks" not in bookmarks[category][page]:
					bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
		state['last_modification']=time.ctime(os.path.getmtime('config.json'))
		state['bookmarks']=bookmarks
		json.dump(state,open('data/state.json','w'),2)
	
	# Load new state
	state = json.load(open('data/state.json','r'),object_pairs_hook=OrderedDict)

	# update current bookmarks
	bookmarks = state['bookmarks']
	newbookmarks = json.load(open('config.json','r'),object_pairs_hook=OrderedDict)
	for category in newbookmarks:
		if category not in bookmarks:
			bookmarks[category] = OrderedDict()
		for page in newbookmarks[category]:
			if page not in bookmarks[category].keys():
				bookmarks[category][page] = newbookmarks[category][page]
				bookmarks[category][page]['last_checked'] = int(time.time()/(60*60*24))
				bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
			else:
				for item in newbookmarks[category][page]:
					bookmarks[category][page][item] = newbookmarks[category][page][item]
								
	# reordering
	reordered = OrderedDict()
	for category in newbookmarks:
		reordered[category] = OrderedDict()
		for page in newbookmarks[category]:
			reordered[category][page] = bookmarks[category][page]
		
	
	state['bookmarks'] = reordered
	state['last_modification']=time.ctime(os.path.getmtime('config.json'))
	

	# Check if redirect is needed
	newsite = path.split('/')
	target_category = 'none'
	target_name = 'none'
	if len(newsite)>1:
		target_category = newsite[0]
		target_name = newsite[1]
	
	
	redirectUrl = ''
	navigation = OrderedDict()
	bookmarks = state['bookmarks']
	for category in bookmarks:
		for page in bookmarks[category]:
			
			# Update the checks from checksAvailable if it matches criteria
			if int(time.time()/(60*60*24))-bookmarks[category][page]['last_checked'] > 0:
				if bookmarks[category][page]['frequency'] == 'daily' or bookmarks[category][page]['frequency'] == day_of_week or (day_of_week=='sunday' and bookmarks[category][page]['frequency']=='weekly') or bookmarks[category][page]['frequency']==day_of_month or (bookmarks[category][page]['frequency']=='monthly' and day_of_month=='10'):
					bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
					bookmarks[category][page]['last_checked'] = int(time.time()/(60*60*24))
				elif int(time.time()/(60*60*24))-bookmarks[category][page]['last_checked'] > 7 and bookmarks[category][page]['frequency']=='weekly':
					bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
					bookmarks[category][page]['last_checked'] = int(time.time()/(60*60*24))
				elif int(time.time()/(60*60*24))-bookmarks[category][page]['last_checked'] > 29 and bookmarks[category][page]['frequency']=='monthly':
					bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
					bookmarks[category][page]['last_checked'] = int(time.time()/(60*60*24))
					
							
			# Determine whether we need to redirect page
			if target_category == category and target_name == page:
				redirectUrl = bookmarks[category][page]['url']
				bookmarks[category][page]['checks'] = bookmarks[category][page]['checks'] - 1

			if bookmarks[category][page]['checks'] > 0:
				if category not in navigation:
					navigation[category] = []
				navigation[category].append({'url':'/' + category + '/' + page, 'name':page, 'title': str(bookmarks[category][page]['checksAvailable']) + 'x ' + bookmarks[category][page]['frequency']})
	
	state['bookmarks']=bookmarks
	json.dump(state,open('data/state.json','w'),indent=4, separators=(',', ': '))
	return navigation,redirectUrl

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	start = time.time()
	redirectUrl = ''
	if 'favicon.ico' in path:
		navigation = {}
		science_feed = {}
		quote = ''
	else:
		navigation,redirectUrl = generate_navigation(path)
		science_feed = getScienceFeed()
		quote = random_line(open('data/quotes.txt'))
		
	#print "Took ",time.time()-start
	if len(redirectUrl)>0:
		return redirect(redirectUrl, code=302)
	else:
		return render_template('index.html',navigation=navigation,quote=quote,science_feed = science_feed)

if __name__ == '__main__':
    app.run(host='152.3.53.178',port=5000)
