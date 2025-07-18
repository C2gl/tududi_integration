class TududiPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.url = 'https://tududi.com'; // Default URL
  }

  connectedCallback() {
    this._fetchConfig();
  }

  async _fetchConfig() {
    try {
      const response = await fetch('/api/tududi_hacs/config');
      if (response.ok) {
        const config = await response.json();
        if (config.url) {
          this.url = config.url;
        }
      }
    } catch (err) {
      console.error('Error fetching Tududi config:', err);
    } finally {
      this._renderIframe();
    }
  }

  _renderIframe() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          height: 100%;
          display: block;
        }
        iframe {
          border: 0;
          width: 100%;
          height: 100%;
        }
      </style>
      <iframe src="${this.url}" allow="fullscreen"></iframe>
    `;
  }
}

customElements.define('tududi-panel', TududiPanel);