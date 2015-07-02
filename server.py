from flask import Flask, render_template, redirect
import json
from datetime import datetime
import time
import os
import filecmp

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	if not os.path.exists('data'):
		os.makedirs('data')
	
	
	if not os.path.isfile('data/config.json.base'):
		os.system('cp config.json data/config.json.base')
		os.system('cp config.json data/bookmarks.json')
	elif not filecmp.cmp('config.json','data/config.json.base'):
		os.system('cp config.json data/config.json.base')
		os.system('cp config.json data/bookmarks.json')
	elif not os.path.isfile('data/bookmarks.json'):
		os.system('cp data/config.json.base data/bookmarks.json')

	bookmarks = json.load(open('data/bookmarks.json','r'))

	
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
	for category in bookmarks:
		for i in range(len(bookmarks[category])):
			
			# check if everything has time stamp
			if "last_checked" not in bookmarks[category][i]:
				bookmarks[category][i]['last_checked'] = time.time()
				json.dump(bookmarks,open('data/bookmarks.json','w'),sort_keys=True,indent=4, separators=(',', ': '))
				
			
			if time.time()-bookmarks[category][i]['last_checked'] > 24*60*60:
				if bookmarks[category][i]['frequency'] == 'daily' or bookmarks[category][i]['frequency'] == day_of_week or (day_of_week=='sunday' and bookmarks[category][i]['frequency']=='weekly') or bookmarks[category][i]['frequency']==day_of_month or (bookmarks[category][i]['frequency']=='monthly' and day_of_month=='10'):
					print bookmarks[category][i]['name']
					bookmarks[category][i]['checks'] = bookmarks[category][i]['checksAvailable']
					bookmarks[category][i]['last_checked'] = time.time()
					json.dump(bookmarks,open('data/bookmarks.json','w'),sort_keys=True,indent=4, separators=(',', ': '))
				
			
			
			if target_category == category and target_name == bookmarks[category][i]['name']:
				redirectUrl = bookmarks[category][i]['url']
				bookmarks[category][i]['checks'] = bookmarks[category][i]['checks'] - 1
				json.dump(bookmarks,open('data/bookmarks.json','w'),sort_keys=True,indent=4, separators=(',', ': '))
				break
			if bookmarks[category][i]['checks'] > 0:
				if category not in navigation:
					navigation[category] = []
				navigation[category].append({'url':'/' + category + '/' + bookmarks[category][i]['name'], 'name':bookmarks[category][i]['name']})
	
				
	if len(redirectUrl)>0:
		return redirect(redirectUrl, code=302)
	else:
		return render_template('index.html',navigation=navigation)

if __name__ == '__main__':
    app.run(host='152.3.53.178',port=5000)
