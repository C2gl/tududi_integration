[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/c2gl/tududi_HACS.svg)](https://github.com/c2gl/tududi_HACS/releases)
[![GitHub issues](https://img.shields.io/github/issues/c2gl/tududi_HACS.svg)](https://github.com/c2gl/tududi_HACS/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/c2gl/tududi_hacs.svg)](https://github.com/c2gl/tududi_hacs/pulls)
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/C2gl/tududi_HACS/total)](https://github.com/c2gl/tududi_HACS/releases)
[![Validate](https://github.com/C2gl/tududi_HACS/actions/workflows/validate.yml/badge.svg)](https://github.com/C2gl/tududi_HACS/actions/workflows/validate.yml)

A HACS integration to add [Tududi](https://github.com/chrisvel/tududi) as a sidebar panel in Home Assistant. 
This integration embeds your Tududi server in a convenient sidebar panel with full configuration through the Home Assistant UI.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=c2gl&repository=tududi_HACS&category=integration)

# Requirements

- **Home Assistant**: Version 2023.1.0 or newer
- **HACS**: Home Assistant Community Store installed
- **Tududi Server**: A running [Tududi](https://github.com/chrisvel/tududi) instance in an external docker. Please follow Tududi's repo linked above with instructions on how to get this running

# Installation 
## HACS Instructions
1. Install HACS in Home Assistant if not already done.
   To do so, please refer to [HACS install guide](https://www.hacs.xyz/docs/use/download/download/#to-download-hacs)
2. Copy the repo URL https://github.com/c2gl/tududi_HACS
3. Add the repo in HACS as a custom repository
4. Search for "Tududi HACS webpanel" in the HACS store
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
   - **Username/Email**: Your Tududi username or email (optional, for todo sensors)
   - **Password**: Your Tududi password (optional, for todo sensors)
5. Click **Submit**

The Tududi panel will automatically appear in your Home Assistant sidebar!

### Sensor Features
If you provide authentication credentials (username/email and password), the integration will also create sensors that track your todos:

- **Next Todo**: Shows your next upcoming todo
- **Upcoming Todos Count**: Number of upcoming todos
- **Today Todos Count**: Number of today's todos

These sensors can be used in dashboards, automations, and notifications. For detailed examples and configuration, see the [Setup Guide](SETUP.md).

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

## SSL/HTTPS Configuration

If you're using HTTPS with self-signed certificates, you may see SSL warnings in the logs. To resolve this:

1. **Recommended**: Use HTTP for local network access (e.g., `http://192.168.1.100:3000`)
2. **Alternative**: Configure your Tududi server with a proper SSL certificate
3. **For advanced users**: You can configure certificate verification in your setup

## Features
- ✅ **Easy Setup**: Configure through Home Assistant UI - no manual file editing needed
- ✅ **Multiple Instances**: Add multiple Tududi servers as separate panels
- ✅ **Customizable**: Set custom panel titles and icons
- ✅ **Todo Sensors**: Track your todos with smart sensors (optional with login)
- ✅ **Auto-Update**: Change settings anytime through the integration options
- ✅ **Clean Uninstall**: Automatically removes panels and files when uninstalled

## Quick Start

Want detailed setup examples and advanced configurations? Check out our [**Setup Guide**](SETUP.md) for:
- Sensor configuration examples
- Dashboard card templates
- Automation ideas
- Troubleshooting tips

## Troubleshooting

### Panel Not Appearing
1. Restart Home Assistant after installation
2. Check **Settings** → **Devices & Services** for proper configuration
3. Verify your Tududi server URL is accessible
4. Clear browser cache and refresh

### Common Issues
- **Integration Not Found**: Make sure HACS is installed and the custom repository is added
- **SSL/HTTPS Warnings**: Use HTTP for local access or ensure proper SSL certificates
- **Iframe Errors**: Check the nginx configuration section above
- **Sensors Not Working**: Provide valid credentials and wait a few minutes for first data fetch

For detailed troubleshooting and advanced configuration, see the [Setup Guide](SETUP.md).

## Updating Configuration
To change your Tududi URL, panel title, or icon:
1. Go to **Settings** → **Devices & Services**
2. Find "Tududi HACS" in your integrations
3. Click **Configure**
4. Update your settings and click **Submit**

The panel will update immediately without requiring a restart.

## Version History

### V0.2.0 
- ✅ **Added**: finaly added to the official HACS store

### v0.1.5
- ✅ **Added**: the use of the tududi api to have custom Home Assistant sensors
- ✅ **Improved**: more issue handeling 

### v0.1.0
- ✅ **Fixed**: Resolved "HomeAssistant object has no attribute 'components'" errors
- ✅ **Improved**: Better frontend component integration
- ✅ **Added**: Minimum Home Assistant version requirement (2023.1.0)
- ✅ **Added**: HA fronted components to have it automatically in sidetab
- ✅ **Enhanced**: More robust panel registration and cleanup

### v0.0.1
- ✅ **Added**: minnimal hand configured webwrap

---

## Contributing

Feel free to contribute by making pull requests! (Don't forget to make your own fork first!)

Sorry if my code is non-working or painful to read - I am not a developer and learning as I go. Any help is welcome and greatly appreciated.

If you have an issue with anything, feel free to let me know in a constructive and respectful way, but keep in mind I was left unsupervised! 😅

### Help to translate 
If you see mistakes in a existing language, or wish to add your language? you can find the language files in "custom_components\tududi_integration\translations". Feel free to fork the repo and make a pull request with your added language.

You can either do this by using the strings folder and adding your language strings. Or you can choose to coppy the "en.json" file that will always be kept up to date with developement of features and retype the strings you want.

When adding a language a workflow will run to check all your strings, please make sure all strings have been completed for your added language before asking for a merge. 

## Bug Reports

Please use the template provided when reporting a bug. If you can, try to provide as much info as possible - it would be great!

## Credits

- This entire project only exists as a bridge for the amazing [Tududi](https://github.com/chrisvel/tududi) project
- Thanks to [HACS.io](https://www.hacs.xyz/) that greatly simplifies distribution and eases the use
- Appreciation to the Home Assistant community for guidance and support
- claudeai to help troubleshoot and explain me how programming works

---

## Support

If you find this integration helpful, pkease consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🤝 Contributing code improvements

**Try to enjoy when not too buggy!** 😅
