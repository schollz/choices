# Check (i.e. *restrain*) How Often I Check (i.e. *inquiry*) Every Site (CHOICES)

This is a tool that is part bookmark manager, part notification system. It is a convenient webpage that you can set to your "Home" page that consists of your bookmarks sorted in categories. However, the bookmarks will disappear based on the number of times you click on them (which is user-configurable) and then they will reappear at a given frequency (also user-configurable). **Thus, it automatically keeps track of when sites are updated and lets you know - and at the same time it makes sure you don't end up visiting the same site over and over every day or over the week.** It also includes an interesting quote - because why not?

Each time you visit the site it will load the new links, and keep the links that haven't been clicked on:

![Before Click](https://i.imgur.com/QqS2klU.jpg)

And once you click on a link (like "Hacker News") it disappears until the next day!

![After Click](https://i.imgur.com/Y8eyXvM.jpg)



## How does it work?

This uses [Flask](http://flask.pocoo.org/) for the web-backend. When a request is made, it uses a confg file - ```config.json``` to reload new bookmarks into the state file ```data/state.json```. This state file contains all the information about how often sites are checked, when they were last checked, how often to update, etc. This is very fast (milliseconds) but relatively simple (i.e. their are probably rampant race condition problems if you want to have concurrency). 

## The configuration file - ```config.json```

The web site loads in the bookmarks from the ```config.json```. This config file holds the categories, pages, and then parameters for how often to reload them (daily, weekly, monthly) and how many checks are allowed during an interval. *The ordering in the config file is the same ordering the website will use.* An example config.json file looks like this: 

```javascript
{
    "Science": {
        "PNAS": {
            "checksAvailable": 2,
            "frequency": "wednesday",
            "url": "http://www.pnas.org/"
        },
        "Nature": {
            "checksAvailable": 2,
            "frequency": "thursday",
            "url": "http://www.nature.com/nature/current_issue.html"
        },
        "Science": {
            "checksAvailable": 2,
            "frequency": "friday",
            "url": "http://www.sciencemag.org/content/current"
        }
    },
    "News": {
        "Hacker News": {
            "checksAvailable": 1,
            "frequency": "daily",
            "url": "https://news.ycombinator.com/"
        },
        "Google News": {
            "checksAvailable": 2,
            "frequency": "daily",
            "url": "https://news.google.com/"
        },
        "New York Times - Science": {
            "checksAvailable": 1,
            "frequency": "weekly",
            "url": "http://www.nytimes.com/section/science"
        },
        "NPR": {
            "checksAvailable": 1,
            "frequency": "daily",
            "url": "http://www.npr.org/sections/news/"
        }
    }
}
```

This loads in the bookmarks as two categories - "Science" and "News" and loads the individual bookmarks in each. The number of checks are ```checksAvailable``` and the frequency is given. The frequencies that you can use are

```bash
"daily" - reloaded each day
"weekly" - reloaded each Sunday
"monthly" - reloaded on the 10th of each month
"day of week" - reloaded on the day of week (monday, tuesday, etc.)
"X" - reloaded on the Xth of each month
```

## Installation

To install, make a config file by copying the basic one or making your own

```bash
cp config.json.default config.json
```

Then you can start the Flask server with

```bash
python choices.py
```

That's it!

### NGINX reverse-proxying with Gunicorn

If you want to host using a reverse proxy with Gunicorn, use the following NGINX conf:


```bash	
server {
	# SERVER BLOCK FOR choices
	listen   80; ## listen for ipv4; this line is default and implied

	access_log /etc/nginx/logs/access-choices.log;
	error_log /etc/nginx/logs/error-choices.log info;
	root /YOURFOLDER;
	server_name YOURURL;
        
   location / {
        proxy_pass http://127.0.0.1:8009;
        proxy_redirect off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

}
```

Then run with 
```bash
nohup gunicorn -b 127.0.0.1:8009 -w 1 -t 600 choices:app &
```


# To-Do

- ~~Automatic update with config.json is update - update a statefile for the app (which carries the timestamp of the last config.json and all the important variables)~~
- ~~Make mobile ready~~
- ~~Add CSS to lists~~
- ~~Add random quote from http://www.quotationspage.com/random.php3 in the top~~
- ~~Set ```last_checked``` to ```floor(time.time()/(60*60*24))```, so that it will easy to determine when its the next day~~
- Handle case when their are no links at all

