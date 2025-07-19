# INFO
A HACS plugin to add [Tududi](https://github.com/chrisvel/tududi) as a sidebar panel in Home Assistant. 
This integration embeds your Tududi server in a convenient sidebar panel with full configuration through the Home Assistant UI.

# Installation 
## HACS Instructions
1. Install HACS in Home Assistant if not already done.
   To do so, please refer to [HACS install guide](https://www.hacs.xyz/docs/use/download/download/#to-download-hacs)
2. Copy the repo URL https://github.com/c2gl/tududi_HACS
3. Add the repo in HACS as a custom repository
4. Search for "TuDuDi HACS webpanel" in the HACS store
5. Install the integration
6. Restart Home Assistant

## Configuration
After installation and restart:

1. Go to **Settings** → **Devices & Services**
2. Click **"+ ADD INTEGRATION"**
3. Search for **"Tududi HACS"**
4. Enter your configuration:
   - **Tududi Server URL**: The full URL to your Tududi server (e.g., `http://192.168.1.100:3000`)
   - **Panel Title**: The title that will appear in the sidebar (default: "Tududi")
   - **Panel Icon**: Material Design Icon name (default: "mdi:clipboard-text")
5. Click **Submit**

The Tududi panel will automatically appear in your Home Assistant sidebar!

### Multiple Instances
You can add multiple Tududi instances by repeating the configuration process with different URLs.

## Manual Configuration (Legacy)
> **Note**: Manual configuration is no longer needed with the new config flow. The integration now handles everything automatically.

If you still prefer manual configuration, you can:
1. Edit the `panel.html` file in `/config/www/tududi_hacs/` to set your URL
2. Add the panel configuration to your `configuration.yaml`

## nginx configuration 
If your Tududi instance is behind NGINX, you might see an error saying that Home Assistant is not permitted to access your Tududi URL. This is because nginx blocks iframe embedding by default. You can work around this by adding these lines to your nginx configuration:

```nginx
add_header X-Frame-Options "ALLOW-FROM [your_home_assistant_url]";
add_header Content-Security-Policy "frame-ancestors 'self' [your_home_assistant_url]";
```

Replace `[your_home_assistant_url]` with your actual Home Assistant URL (e.g., `http://homeassistant.local:8123`).

## Features
- ✅ **Easy Setup**: Configure through Home Assistant UI - no manual file editing needed
- ✅ **Multiple Instances**: Add multiple Tududi servers as separate panels
- ✅ **Customizable**: Set custom panel titles and icons
- ✅ **Auto-Update**: Change settings anytime through the integration options
- ✅ **Clean Uninstall**: Automatically removes panels and files when uninstalled

## Troubleshooting

### Panel Not Appearing
1. Make sure you've restarted Home Assistant after installation
2. Check that the integration is properly configured in **Settings** → **Devices & Services**
3. Verify your Tududi server URL is accessible from your Home Assistant instance

### Iframe Errors
- If you see "X-Frame-Options" errors, check the nginx configuration section above
- Ensure your Tududi server allows iframe embedding
- Test the URL directly in a browser to confirm it's accessible

### Multiple Instances
Each Tududi URL can only be configured once. If you want to add the same server with different settings, you'll need to use a slightly different URL (e.g., add a query parameter).

## Updating Configuration
To change your Tududi URL, panel title, or icon:
1. Go to **Settings** → **Devices & Services**
2. Find "Tududi HACS" in your integrations
3. Click **Configure**
4. Update your settings and click **Submit**

The panel will update immediately without requiring a restart.

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