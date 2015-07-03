# Check How Often I Check Every Site (CHOICES)

Instead of a bookmark manager, this is a tool that hosts all your bookmarks - but only shows the ones that you haven't checked recently. Bookmarks can be set to check every day, week, month, year - any number of times.

# To-Do

- ~Automatic update with config.json is update - update a statefile for the app (which carries the timestamp of the last config.json and all the important variables)~
- ~Make mobile ready~
- Add CSS to lists
- Add random quote from http://www.quotationspage.com/random.php3 in the top
- Handle case when their are no links at all

# To run

Add this NGINX configuration:

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
