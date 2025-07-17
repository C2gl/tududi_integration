# INFO
a little HACS plugin to add [Tududi](https://github.com/chrisvel/tududi) as sidebar pannel in home assistant 
all this will do is embed an exteral docker-hosted webpage


# installation 
## HACS instructions
Install HACS in home assistant if not already done.
To do so, please refer to [HACS install guide](https://www.hacs.xyz/docs/use/download/download/#to-download-hacs)
Copy the repo url https://github.com/c2gl/tududi_HACS
Paste the repo in hacs
Search for tududi_HACS in the HASC store
Install the app 
once installed, you should use visual studio plugin to eddit some configurations manually

## configurations
once tududi_hacs is installed you should restart home assistant.

After this restart, you can head to `setings -> devices & services -> add integration` 
Here you can look for **tududi HACS webpanel** and when adding said integration, it will prompt you for the tududi url.


you are also to add the code in [configuration.yaml](https://github.com/C2gl/tududi_HACS/blob/main/configuration.yaml) to the `configuration.yaml` file in your home assistant to display the new tab in the sidebar. its also here that you can eddit the title and icon to your own liking.

## nginx configuration 
if your tududi instance is behind NGINX, you probably will see an error telling you that home assistant is not permitted to the url of your tududi. 
this is because nginx blocks iframe by default. this can be worked around by adding these lines to your config or advanced settings 

```yaml
add_header X-Frame-Options "ALLOW-FROM [your_home_assistant_url]";
add_header Content-Security-Policy "frame-ancestors 'self' [your_home_assistant_url]";
```

# Try to enjoy when not too buggy 😅

# bug reports
please use the template provided when reporting a bug, 
if you can, trying to provide as much info as possible would be great 

# helping out the project
feel free to try and help by making your pull request, (don't forget to make your own fork first!)

sorry if my code is non working or painfull to read, i am not a def and learning as i do. anny help is welcome and greatly apreciated.

if you have a issue with anything, feel free to let me know in a constructive and respectfull way. but keep in mind i was left unsupervised

# credits where credits are due
- this entire prokect only exists as a bridge for the previously amazing [Tududi](https://github.com/chrisvel/tududi) project
- the use of [HACS.io](https://www.hacs.xyz/) that greatly simplifies this and eases the use