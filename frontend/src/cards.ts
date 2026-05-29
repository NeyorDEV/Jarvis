/**
 * J.A.R.V.I.S — Dynamic Contextual Cards
 * Handles creation and animation of transient information cards.
 */

export interface CardOptions {
  id?: string;
  title: string;
  type?: 'info' | 'system' | 'media' | 'alert' | 'search';
  content: string;
  duration?: number; // ms, default 10000
  icon?: string;
}

class CardManager {
  private container: HTMLElement | null = null;

  constructor() {
    this.container = document.getElementById('cards-hud');
  }

  public showCard(options: CardOptions) {
    if (!this.container) return;

    const id = options.id || `card-${Date.now()}`;
    const duration = options.duration || 10000;
    
    // Remove existing card with same ID if any
    const existing = document.getElementById(id);
    if (existing) existing.remove();

    const card = document.createElement('div');
    card.id = id;
    card.className = `ctx-card ctx-card-${options.type || 'info'}`;
    
    const iconHtml = options.icon ? `<div class="ctx-card-icon">${options.icon}</div>` : '';

    card.innerHTML = `
<div class="ctx-card-header">
${iconHtml}
<div class="ctx-card-title">${options.title.toUpperCase()}</div>
<div class="ctx-card-close">✕</div>
</div>
<div class="ctx-card-body">${options.content}</div>
<div class="ctx-card-progress">
<div class="ctx-card-progress-bar" style="animation-duration: ${duration}ms"></div>
</div>
<div class="ctx-card-glow"></div>
`;

    this.container.appendChild(card);

    // Trigger animation
    requestAnimationFrame(() => {
      card.classList.add('visible');
    });

    // Close logic
    const closeBtn = card.querySelector('.ctx-card-close');
    closeBtn?.addEventListener('click', () => this.dismissCard(card));

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => {
        if (card.parentElement) this.dismissCard(card);
      }, duration);
    }
  }

  private dismissCard(card: HTMLElement) {
    card.classList.remove('visible');
    card.classList.add('dismiss');
    setTimeout(() => {
      card.remove();
    }, 600);
  }
}

export const cardManager = new CardManager();
