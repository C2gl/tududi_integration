class TududiIframeView(HomeAssistantView):
    """View for serving the Tududi iframe."""

    requires_auth = False
    url = "/tududi/iframe"
    name = "tududi:iframe"

    async def get(self, request):
        """Return the iframe to the Tududi website."""
        # Get the first config entry
        entries = request.app["hass"].config_entries.async_entries(DOMAIN)
        if entries:
            url = entries[0].data.get("url", "https://tududi.com")
        else:
            url = "https://tududi.com"
            
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tududi</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                }}
                iframe {{
                    width: 100%;
                    height: 100%;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <iframe src="{url}" allow="fullscreen"></iframe>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")