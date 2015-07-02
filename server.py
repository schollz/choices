from flask import Flask, render_template, redirect
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	navigation = json.load(open('config.json','r'))
	print 'You want path: %s' % path
	newsite = path.split('/')
	redirectUrl = ''
	if len(newsite)>1:
		for i in range(len(navigation[newsite[0]])):
			if newsite[1]==navigation[newsite[0]][i]['name']:
				redirectUrl =  navigation[newsite[0]][i]['url']
				navigation[newsite[0]][i]['checks'] = navigation[newsite[0]][i]['checks']-1
				json.dump(navigation,open('config.json','w'))
				break
				
	if len(redirectUrl)>0:
		return redirect(redirectUrl, code=302)
	else:
		return render_template('index.html',navigation=navigation)

if __name__ == '__main__':
    app.run(host='152.3.53.178',port=5000)
