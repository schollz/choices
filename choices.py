from flask import Flask, render_template, redirect
import json
from datetime import datetime
import time
import os
import filecmp

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	start = time.time()
	state = {}
	if not os.path.exists('data'):
		os.makedirs('data')
	
	print state
	print time.ctime(os.path.getmtime('config.json'))
	if not os.path.isfile('data/state.json'):
		bookmarks = json.load(open('config.json','r'))
		for category in bookmarks:
			for page in bookmarks[category]:
				
				# check if everything has time stamp
				if "last_checked" not in bookmarks[category][page]:
					bookmarks[category][page]['last_checked'] = time.time()
					json.dump(bookmarks,open('data/bookmarks.json','w'),sort_keys=True,indent=4, separators=(',', ': '))
				
				if "checks" not in bookmarks[category][page]:
					bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
		state['last_modification']=time.ctime(os.path.getmtime('config.json'))
		state['bookmarks']=bookmarks
		json.dump(state,open('data/state.json','w'),2)
	
	# Load new state
	state = json.load(open('data/state.json','r'))
	print state
	
	if 'last_modification' not in state or state['last_modification'] != time.ctime(os.path.getmtime('config.json')):
		# update current bookmarks
		bookmarks = state['bookmarks']
		newbookmarks = json.load(open('config.json','r'))
		for category in newbookmarks:
			if category not in bookmarks:
				bookmarks[category] = {}				
				for page in bookmarks[category]:
					bookmarks[category][page] = newbookmarks[category][page]
			else:
				for page in newbookmarks[category]:
					if page not in bookmarks[category]:
						bookmarks[category][page] = newbookmarks[category][page]
						bookmarks[category][page]['last_checked'] = time.time()
						bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
					else:
						for item in newbookmarks[category][page]:
							if bookmarks[category][page][item] != newbookmarks[category][page][item]:
								bookmarks[category][page][item] = newbookmarks[category][page][item]
			
		state['last_modification']=time.ctime(os.path.getmtime('config.json'))
	
	

	
	day_of_week = datetime.now().strftime('%A').lower()
	day_of_month = str(int(datetime.now().strftime('%d')))

	# Check if redirect is needed
	newsite = path.split('/')
	target_category = 'none'
	target_name = 'none'
	if len(newsite)>1:
		target_category = newsite[0]
		target_name = newsite[1]
	
	
	redirectUrl = ''
	navigation = {}
	bookmarks = state['bookmarks']
	for category in bookmarks:
		for page in bookmarks[category]:
			
			# Update the checks from checksAvailable if it matches criteria
			if time.time()-bookmarks[category][page]['last_checked'] > 24*60*60:
				if bookmarks[category][page]['frequency'] == 'daily' or bookmarks[category][page]['frequency'] == day_of_week or (day_of_week=='sunday' and bookmarks[category][page]['frequency']=='weekly') or bookmarks[category][page]['frequency']==day_of_month or (bookmarks[category][page]['frequency']=='monthly' and day_of_month=='10'):
					bookmarks[category][page]['checks'] = bookmarks[category][page]['checksAvailable']
					bookmarks[category][page]['last_checked'] = time.time()
							
			# Determine whether we need to redirect page
			if target_category == category and target_name == page:
				redirectUrl = bookmarks[category][page]['url']
				bookmarks[category][page]['checks'] = bookmarks[category][page]['checks'] - 1
				break
			if bookmarks[category][page]['checks'] > 0:
				if category not in navigation:
					navigation[category] = []
				navigation[category].append({'url':'/' + category + '/' + page, 'name':page})
	
	state['bookmarks']=bookmarks
	json.dump(state,open('data/state.json','w'),sort_keys=True,indent=4, separators=(',', ': '))

	print "Took ",time.time()-start
	if len(redirectUrl)>0:
		return redirect(redirectUrl, code=302)
	else:
		return render_template('index.html',navigation=navigation)

if __name__ == '__main__':
    app.run(host='152.3.53.178',port=5000)
