class TududiPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
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
      <iframe src="https://tududi.com"></iframe>
    `;
  }
}

customElements.define('tududi-panel', TududiPanel);