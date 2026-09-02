/**
 * AURA Real Estate - Core Application Architecture Script
 * Version: 2.4.0
 * Senior Lead Developer Swarm - JARVIS Edition
 * 
 * Modules:
 * - Toast Notification System
 * - Sticky Header & Mobile Drawer Navigation
 * - Dynamic Statistic Counters (IntersectionObserver)
 * - Favorites / Wishlist LocalStorage Manager
 * - Interactive Property Database & Quick View Modal Manager
 * - Advanced Listings Filter, Sorting & View Mode Switcher (Grid / List)
 * - FAQ Interactive Live Search & Category Filter
 * - Interactive Map Pins & Office Selector Sync
 * - Form Validation & Confidential Lead Capture
 * - Smooth Scroll & Motion Reveal Observers
 */

'use strict';

// Polyfill / Environment Guard for Node.js Sandbox Execution
if (typeof window === 'undefined') {
    const safeGlobal = typeof globalThis !== 'undefined' ? globalThis : global;
    safeGlobal.window = safeGlobal;
    if (!safeGlobal.window.location) safeGlobal.window.location = { search: '' };
    if (!safeGlobal.window.addEventListener) safeGlobal.window.addEventListener = () => {};
    if (!safeGlobal.window.removeEventListener) safeGlobal.window.removeEventListener = () => {};
}

// Global AURA State Manager
window.AURA_APP = window.AURA_APP || {
    favorites: [],
    propertiesData: {},
    currentFilters: {
        keyword: '',
        quickTag: 'all',
        transaction: 'all',
        location: 'all',
        category: 'all',
        price: 'all',
        bedrooms: 'all'
    },
    sortOption: 'featured',
    viewMode: 'grid'
};

if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        AURA.init();
    });
}

const AURA = {
    init() {
        this.initCurrentYear();
        this.initToastSystem();
        this.initHeaderAndDrawer();
        this.initFavoritesManager();
        this.initCounterObserver();
        this.initPropertiesDatabase();
        this.initPropertyModal();
        this.initCatalogFiltersAndSort();
        this.initFaqInteractive();
        this.initContactMapAndOffices();
        this.initFormHandlers();
        this.initScrollReveal();
    },

    /* ==========================================================================
       1. CURRENT YEAR AUTOMATIC UPDATER
       ========================================================================== */
    initCurrentYear() {
        if (typeof document === 'undefined') return;
        const yearElem = document.getElementById('currentYear');
        if (yearElem) {
            yearElem.textContent = new Date().getFullYear();
        }
    },

    /* ==========================================================================
       2. TOAST NOTIFICATION SYSTEM
       ========================================================================== */
    initToastSystem() {
        window.showToast = (message, type = 'info', duration = 4000) => {
            if (typeof document === 'undefined') return;
            const container = document.getElementById('toastContainer');
            if (!container) return;

            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            
            let iconSymbol = 'ℹ';
            if (type === 'success') iconSymbol = '✓';
            if (type === 'error') iconSymbol = '⚠';

            toast.innerHTML = `
                <span class="toast-icon">${iconSymbol}</span>
                <span class="toast-message">${message}</span>
                <button type="button" class="toast-close" aria-label="Fermer la notification">&times;</button>
            `;

            const closeBtn = toast.querySelector('.toast-close');
            const dismissToast = () => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(50px)';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.parentNode.removeChild(toast);
                    }
                }, 300);
            };

            closeBtn.addEventListener('click', dismissToast);
            container.appendChild(toast);

            setTimeout(() => {
                dismissToast();
            }, duration);
        };
    },

    /* ==========================================================================
       3. STICKY HEADER & MOBILE DRAWER NAVIGATION
       ========================================================================== */
    initHeaderAndDrawer() {
        if (typeof document === 'undefined') return;
        const header = document.getElementById('header');
        const mobileToggle = document.getElementById('mobileToggle');
        const mobileMenu = document.getElementById('mobileMenu');
        const drawerClose = document.getElementById('drawerClose');

        // Sticky Header Transition on Scroll
        if (header) {
            const handleScroll = () => {
                if (window.scrollY > 40) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            };
            window.addEventListener('scroll', handleScroll, { passive: true });
            handleScroll();
        }

        // Mobile Drawer Controls
        if (mobileToggle && mobileMenu) {
            const openDrawer = () => {
                mobileToggle.classList.add('active');
                mobileToggle.setAttribute('aria-expanded', 'true');
                mobileMenu.classList.add('active');
                mobileMenu.setAttribute('aria-hidden', 'false');
                document.body.style.overflow = 'hidden';
            };

            const closeDrawer = () => {
                mobileToggle.classList.remove('active');
                mobileToggle.setAttribute('aria-expanded', 'false');
                mobileMenu.classList.remove('active');
                mobileMenu.setAttribute('aria-hidden', 'true');
                document.body.style.overflow = '';
            };

            mobileToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = mobileMenu.classList.contains('active');
                if (isOpen) {
                    closeDrawer();
                } else {
                    openDrawer();
                }
            });

            if (drawerClose) {
                drawerClose.addEventListener('click', closeDrawer);
            }

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
                    closeDrawer();
                }
            });

            // Close when clicking nav links in mobile drawer
            const drawerLinks = mobileMenu.querySelectorAll('a');
            drawerLinks.forEach(link => {
                link.addEventListener('click', () => {
                    closeDrawer();
                });
            });
        }
    },

    /* ==========================================================================
       4. FAVORITES / WISHLIST LOCALSTORAGE MANAGER
       ========================================================================== */
    initFavoritesManager() {
        try {
            if (typeof localStorage !== 'undefined') {
                const stored = localStorage.getItem('aura_favorites');
                if (stored) {
                    window.AURA_APP.favorites = JSON.parse(stored);
                }
            }
        } catch (e) {
            console.warn('LocalStorage non accessible pour les favoris.');
        }

        const updateFavoriteUI = () => {
            if (typeof document === 'undefined') return;
            const favButtons = document.querySelectorAll('.favorite-btn');
            favButtons.forEach(btn => {
                const propId = btn.getAttribute('data-property-id');
                if (window.AURA_APP.favorites.includes(propId)) {
                    btn.classList.add('active');
                    btn.innerHTML = '&#9829;'; // Filled heart symbol
                    btn.style.color = '#D4AF37';
                } else {
                    btn.classList.remove('active');
                    btn.innerHTML = '&#9825;'; // Empty heart symbol
                    btn.style.color = '';
                }
            });
        };

        if (typeof document !== 'undefined') {
            // Event delegation for favorite buttons
            document.addEventListener('click', (e) => {
                const favBtn = e.target.closest('.favorite-btn');
                if (!favBtn) return;

                e.preventDefault();
                e.stopPropagation();

                const propId = favBtn.getAttribute('data-property-id');
                if (!propId) return;

                const index = window.AURA_APP.favorites.indexOf(propId);
                if (index > -1) {
                    window.AURA_APP.favorites.splice(index, 1);
                    if (window.showToast) {
                        window.showToast('Propriété retirée de vos favoris.', 'info');
                    }
                } else {
                    window.AURA_APP.favorites.push(propId);
                    if (window.showToast) {
                        window.showToast('Propriété ajoutée à votre sélection privée !', 'success');
                    }
                }

                try {
                    if (typeof localStorage !== 'undefined') {
                        localStorage.setItem('aura_favorites', JSON.stringify(window.AURA_APP.favorites));
                    }
                } catch (err) {
                    console.warn('Impossible de sauvegarder les favoris.');
                }

                updateFavoriteUI();
            });
        }

        updateFavoriteUI();
    },

    /* ==========================================================================
       5. DYNAMIC STATISTIC COUNTERS (IntersectionObserver)
       ========================================================================== */
    initCounterObserver() {
        if (typeof document === 'undefined' || typeof IntersectionObserver === 'undefined') return;
        const counterElems = document.querySelectorAll('.stat-counter');
        if (counterElems.length === 0) return;

        const animateCounter = (el) => {
            const target = parseFloat(el.getAttribute('data-target') || '0');
            const decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
            const duration = 2200; // ms
            const startTime = typeof performance !== 'undefined' ? performance.now() : Date.now();

            const step = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Ease Out Quartic
                const easeProgress = 1 - Math.pow(1 - progress, 4);
                const currentVal = easeProgress * target;

                el.textContent = currentVal.toFixed(decimals);

                if (progress < 1) {
                    if (typeof requestAnimationFrame !== 'undefined') {
                        requestAnimationFrame(step);
                    } else {
                        setTimeout(() => step(Date.now()), 16);
                    }
                } else {
                    el.textContent = target.toFixed(decimals);
                }
            };

            if (typeof requestAnimationFrame !== 'undefined') {
                requestAnimationFrame(step);
            } else {
                step(startTime);
            }
        };

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });

        counterElems.forEach(el => observer.observe(el));
    },

    /* ==========================================================================
       6. INTERACTIVE PROPERTIES DATABASE & QUICK VIEW MODAL
       ========================================================================== */
    initPropertiesDatabase() {
        window.AURA_APP.propertiesData = {
            'prop-01': {
                id: 'prop-01',
                title: 'Villa Horizon & Panoramas Maritimes',
                location: 'Monaco • Cap d\'Ail',
                price: '24 500 000 €',
                img: 'https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Vérifié & Validé', class: 'badge-emerald' },
                    { text: 'Off-Market', class: 'badge-gold' }
                ],
                specs: '650 m² habitables • 6 Suites • 1 200 m² Jardin • Accès mer direct',
                desc: 'Suspendue entre ciel et mer à la frontière immédiate de Monaco, la Villa Horizon incarne l\'excellence architecturale contemporaine. Développée sur trois niveaux baignés de lumière avec parois de verre pleine hauteur, elle dispose d\'un héliport privé, d\'un spa holistique et d\'une piscine à débordement chauffée miroitant sur le large.',
                tags: ['Vue Mer 180°', 'Piscine Débordement', 'Spa & Sauna', 'Ascenseur Privé', 'Héliport', 'Garages 6 Véhicules']
            },
            'prop-02': {
                id: 'prop-02',
                title: 'Penthouse Duplex Triangle d\'Or',
                location: 'Paris 8ème • Avenue Montaigne',
                price: '18 200 000 €',
                img: 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Exclusivité AURA', class: 'badge-gold' }
                ],
                specs: '380 m² habitables • 4 Suites • 150 m² Terrasse d\'angle',
                desc: 'Niché au dernier étage d\'un immeuble haussmannien de grand standing sécurisé avec gardiennage 24/7, ce penthouse d\'exception allie boiseries dorées restaurées et aménagements haute technologie. Sa terrasse plein ciel de 150 m² embrasse une vue à 360° sur la Tour Eiffel et l\'Avenue Montaigne.',
                tags: ['Vue Tour Eiffel', 'Terrasse Plein Ciel', 'Domotique Lutron', 'Suite Royale 90m²', 'Sécurité 24/7']
            },
            'prop-03': {
                id: 'prop-03',
                title: 'Domaine Contemporain Lémanique',
                location: 'Genève • Cologny',
                price: '31 000 000 CHF',
                img: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Mandat Confidentiel', class: 'badge-indigo' }
                ],
                specs: '920 m² habitables • 8 Suites • 5 000 m² Parc paysager',
                desc: 'Au cœur de la commune la plus prisée du canton de Genève, cette résidence d\'architecte se déploie dans un parc botanique privé bordant le Lac Léman. Équipée d\'un ponton d\'amarrage privé, d\'un bassin olympique intérieur et d\'une cave à vin sécurisée sous digicode pour 2 000 flacons.',
                tags: ['Ponton Privé', 'Piscine Intérieure', 'Cave 2000 Flacons', 'Home Cinéma 4K', 'Logement de Personnel']
            },
            'prop-04': {
                id: 'prop-04',
                title: 'Sky Villa & Marina Privée',
                location: 'Dubaï • Palm Jumeirah',
                price: '29 800 000 $',
                img: 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Off-Market VIP', class: 'badge-emerald' }
                ],
                specs: '750 m² habitables • 5 Suites • Piscine suspendue en verre',
                desc: 'Occupant le sommet d\'une tour emblématique signée par un studio international, cette Sky Villa jouit d\'un panorama complet sur le Golfe Arabique et l\'horizon de Dubaï. Finitions en marbre d\'Eramosa, ameublement sur-mesure SAOTA et service de majordome dédié 24/7.',
                tags: ['Piscine Suspendue', 'Majordome 24/7', 'Ascenseur Privatif Direct', 'Marina Privée', 'Ameublement SAOTA']
            },
            'prop-05': {
                id: 'prop-05',
                title: 'Hôtel Particulier & Jardin Secret',
                location: 'Paris 16ème • Avenue Foch',
                price: '38 000 000 €',
                img: 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Patrimoine Rare', class: 'badge-gold' }
                ],
                specs: '1 100 m² habitables • 9 Suites • 400 m² Jardin arboré',
                desc: 'Véritable havre de paix confidentiel à l\'abri des regards, cet hôtel particulier d\'époque Napoléon III a fait l\'objet d\'une réhabilitation totale de 3 ans. Il intègre un espace bien-être d\'inspiration romaine avec hammam, salle de projection privée et appartement pour le personnel.',
                tags: ['Jardin Arboré', 'Espace Hammam & Spa', 'Cinéma Dolby Atmos', 'Chambre Blindée', 'Parkings Couverts']
            },
            'prop-06': {
                id: 'prop-06',
                title: 'Villa Waterfront Pieds dans l\'Eau',
                location: 'Côte d\'Azur • Saint-Jean-Cap-Ferrat',
                price: '42 000 000 €',
                img: 'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Pieds dans l\'Eau', class: 'badge-emerald' }
                ],
                specs: '820 m² habitables • 7 Suites • Accès direct mer & ponton',
                desc: 'Située à la pointe la plus exclusive de la presqu\'île de Saint-Jean-Cap-Ferrat, cette résidence de maître bénéficie d\'une intégration organique exceptionnelle dans les roches méditerranéennes. Accès mer privé, garage à bicyclettes nautiques et maison d\'invités indépendante.',
                tags: ['Accès Mer Direct', 'Ponton Bateau', 'Maison d\'Invités', 'Jardin Méditerranéen', 'Sécurité Renforcée']
            },
            'prop-07': {
                id: 'prop-07',
                title: 'Résidence Belvédère & Solarium Privé',
                location: 'Monaco • Jardin Exotique',
                price: '27 900 000 €',
                img: 'https://images.unsplash.com/photo-1502877338535-766e1452684a?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Confidentiel', class: 'badge-indigo' }
                ],
                specs: '540 m² habitables • 5 Suites • 220 m² Roof-Top Solarium',
                desc: 'Une adresse d\'une rareté absolue dominant la Principauté de Monaco. Ce triplex d\'architecte offre un solarium d\'exception sur le toit équipé d\'un jacuzzi chauffé et d\'une cuisine d\'été extérieure surplombant le Rocher et le Port Hercule.',
                tags: ['Vue Rocher & Port', 'Roof-Top Jacuzzi', 'Cuisine d\'Été Extérieure', '4 Parkings Sécurisés', 'Services de Conciergerie']
            },
            'prop-08': {
                id: 'prop-08',
                title: 'Bastide Provençale & Vignoble Privé',
                location: 'Côte d\'Azur • Saint-Tropez',
                price: '19 500 000 €',
                img: 'https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?w=800&auto=format&fit=crop',
                badges: [
                    { text: 'Domaine d\'Exception', class: 'badge-gold' }
                ],
                specs: '700 m² habitables • 6 Suites • 30 000 m² Domaine & Vignes',
                desc: 'À quelques minutes de la mythique plage de Pampelonne, ce domaine séculaire s\'étend sur 3 hectares de vignobles d\'AOP et d\'oliviers centenaires. Bastide entièrement réinventée dans un luxe épuré, disposant d\'un helipad homologué et d\'écuries privées.',
                tags: ['Vignoble d\'AOP', 'Héliport Homologué', 'Écuries', 'Cazal d\'Invités', 'Piscine Chauffée 20m']
            }
        };

        // Fallback mapping for homepage property numbers '01', '02', '03', '04'
        window.AURA_APP.propertiesData['01'] = window.AURA_APP.propertiesData['prop-01'];
        window.AURA_APP.propertiesData['02'] = window.AURA_APP.propertiesData['prop-02'];
        window.AURA_APP.propertiesData['03'] = window.AURA_APP.propertiesData['prop-03'];
        window.AURA_APP.propertiesData['04'] = window.AURA_APP.propertiesData['prop-04'];
    },

    initPropertyModal() {
        if (typeof document === 'undefined') return;
        const modal = document.getElementById('propertyModal');
        const modalCloseBtn = document.getElementById('modalCloseBtn');
        if (!modal) return;

        const openModal = (propId) => {
            const data = window.AURA_APP.propertiesData[propId];
            if (!data) {
                console.warn(`Propriété non trouvée pour l'ID: ${propId}`);
                return;
            }

            const imgEl = document.getElementById('modalImg');
            const badgesEl = document.getElementById('modalBadges');
            const locationEl = document.getElementById('modalLocation');
            const titleEl = document.getElementById('modalTitle');
            const priceEl = document.getElementById('modalPrice');
            const specsEl = document.getElementById('modalSpecs');
            const descEl = document.getElementById('modalDescriptionText');
            const tagsEl = document.getElementById('modalTags');
            const contactLink = document.getElementById('modalContactLink');

            if (imgEl) {
                imgEl.src = data.img;
                imgEl.alt = data.title;
            }
            if (locationEl) locationEl.textContent = data.location;
            if (titleEl) titleEl.textContent = data.title;
            if (priceEl) priceEl.textContent = data.price;
            if (specsEl) specsEl.textContent = data.specs;
            if (descEl) descEl.textContent = data.desc;

            if (badgesEl) {
                badgesEl.innerHTML = data.badges.map(b => `<span class="badge ${b.class}">${b.text}</span>`).join('');
            }

            if (tagsEl) {
                tagsEl.innerHTML = data.tags.map(t => `<span class="f-tag">${t}</span>`).join('');
            }

            if (contactLink) {
                contactLink.href = `contact.html?ref=${data.id}&subject=offmarket`;
            }

            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        };

        const closeModal = () => {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        };

        // Event delegation for opening quick view modal
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('.open-modal-trigger');
            if (trigger) {
                e.preventDefault();
                const propId = trigger.getAttribute('data-property-id');
                if (propId) {
                    openModal(propId);
                }
            }
        });

        if (modalCloseBtn) {
            modalCloseBtn.addEventListener('click', closeModal);
        }

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });
    },

    /* ==========================================================================
       7. ADVANCED CATALOG FILTERING, SORTING & VIEW SWITCHER (annonces.html)
       ========================================================================== */
    initCatalogFiltersAndSort() {
        if (typeof document === 'undefined') return;
        const filterForm = document.getElementById('listingsFilterForm');
        const catalogContainer = document.getElementById('propertiesCatalog');
        const noResultsState = document.getElementById('noResultsState');
        const resultsCountEl = document.getElementById('resultsCount');

        if (!catalogContainer) return; // Not on catalog page or grid missing

        const viewGridBtn = document.getElementById('viewGridBtn');
        const viewListBtn = document.getElementById('viewListBtn');
        const catalogSort = document.getElementById('catalogSort');

        // View Mode Switcher
        if (viewGridBtn && viewListBtn) {
            viewGridBtn.addEventListener('click', () => {
                viewGridBtn.classList.add('active');
                viewListBtn.classList.remove('active');
                catalogContainer.classList.remove('mode-list');
                catalogContainer.classList.add('mode-grid');
                window.AURA_APP.viewMode = 'grid';
            });

            viewListBtn.addEventListener('click', () => {
                viewListBtn.classList.add('active');
                viewGridBtn.classList.remove('active');
                catalogContainer.classList.remove('mode-grid');
                catalogContainer.classList.add('mode-list');
                window.AURA_APP.viewMode = 'list';
            });
        }

        // Apply Filters Function
        const applyFilters = () => {
            const cards = Array.from(catalogContainer.querySelectorAll('.property-card'));
            let visibleCount = 0;

            const state = window.AURA_APP.currentFilters;

            cards.forEach(card => {
                const cardTx = card.getAttribute('data-transaction') || '';
                const cardLoc = card.getAttribute('data-location') || '';
                const cardCat = card.getAttribute('data-category') || '';
                const cardPrice = parseInt(card.getAttribute('data-price') || '0', 10);
                const cardBeds = parseInt(card.getAttribute('data-bedrooms') || '0', 10);
                const cardTitle = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
                const cardDesc = card.querySelector('.card-short-desc')?.textContent.toLowerCase() || '';
                const cardLocText = card.querySelector('.card-location')?.textContent.toLowerCase() || '';

                let matches = true;

                // Keyword match
                if (state.keyword && state.keyword.trim() !== '') {
                    const kw = state.keyword.toLowerCase().trim();
                    const textContent = `${cardTitle} ${cardDesc} ${cardLocText}`;
                    if (!textContent.includes(kw)) {
                        matches = false;
                    }
                }

                // Quick Tag Match
                if (matches && state.quickTag !== 'all') {
                    if (state.quickTag === 'offmarket' && !cardTx.includes('offmarket')) matches = false;
                    if (state.quickTag === 'penthouse' && cardCat !== 'penthouse') matches = false;
                    if (state.quickTag === 'villa' && cardCat !== 'villa') matches = false;
                }

                // Transaction Match
                if (matches && state.transaction !== 'all') {
                    if (!cardTx.includes(state.transaction)) matches = false;
                }

                // Location Match
                if (matches && state.location !== 'all') {
                    if (cardLoc !== state.location) matches = false;
                }

                // Category Match
                if (matches && state.category !== 'all') {
                    if (cardCat !== state.category) matches = false;
                }

                // Price Match
                if (matches && state.price !== 'all') {
                    if (state.price === 'under-15m' && cardPrice >= 15000000) matches = false;
                    if (state.price === '15m-25m' && (cardPrice < 15000000 || cardPrice > 25000000)) matches = false;
                    if (state.price === '25m-35m' && (cardPrice < 25000000 || cardPrice > 35000000)) matches = false;
                    if (state.price === 'above-35m' && cardPrice <= 35000000) matches = false;
                }

                // Bedrooms Match
                if (matches && state.bedrooms !== 'all') {
                    if (state.bedrooms === '3+' && cardBeds < 3) matches = false;
                    if (state.bedrooms === '5+' && cardBeds < 5) matches = false;
                    if (state.bedrooms === '7+' && cardBeds < 7) matches = false;
                }

                if (matches) {
                    card.classList.remove('hidden');
                    visibleCount++;
                } else {
                    card.classList.add('hidden');
                }
            });

            if (resultsCountEl) {
                resultsCountEl.textContent = visibleCount;
            }

            if (noResultsState) {
                if (visibleCount === 0) {
                    noResultsState.classList.remove('hidden');
                } else {
                    noResultsState.classList.add('hidden');
                }
            }

            sortCatalogCards();
        };

        // Sort Cards Algorithm
        const sortCatalogCards = () => {
            const cards = Array.from(catalogContainer.querySelectorAll('.property-card'));
            const option = window.AURA_APP.sortOption;

            cards.sort((a, b) => {
                const priceA = parseInt(a.getAttribute('data-price') || '0', 10);
                const priceB = parseInt(b.getAttribute('data-price') || '0', 10);
                const surfA = parseInt(a.getAttribute('data-surface') || '0', 10);
                const surfB = parseInt(b.getAttribute('data-surface') || '0', 10);

                if (option === 'price-desc') return priceB - priceA;
                if (option === 'price-asc') return priceA - priceB;
                if (option === 'surface-desc') return surfB - surfA;
                return 0; // Default featured order
            });

            cards.forEach(card => catalogContainer.appendChild(card));
        };

        // Event Listeners for Filter Inputs
        const keywordInput = document.getElementById('filter-keyword');
        const txSelect = document.getElementById('filter-transaction');
        const locSelect = document.getElementById('filter-location');
        const catSelect = document.getElementById('filter-category');
        const priceSelect = document.getElementById('filter-price');
        const bedsSelect = document.getElementById('filter-bedrooms');
        const quickTagBtns = document.querySelectorAll('.quick-tag-btn');
        const resetBtn = document.getElementById('resetFiltersBtn');
        const resetAllBtns = document.querySelectorAll('.btn-reset-all');

        if (keywordInput) {
            keywordInput.addEventListener('input', (e) => {
                window.AURA_APP.currentFilters.keyword = e.target.value;
                applyFilters();
            });
        }

        if (txSelect) {
            txSelect.addEventListener('change', (e) => {
                window.AURA_APP.currentFilters.transaction = e.target.value;
                applyFilters();
            });
        }

        if (locSelect) {
            locSelect.addEventListener('change', (e) => {
                window.AURA_APP.currentFilters.location = e.target.value;
                applyFilters();
            });
        }

        if (catSelect) {
            catSelect.addEventListener('change', (e) => {
                window.AURA_APP.currentFilters.category = e.target.value;
                applyFilters();
            });
        }

        if (priceSelect) {
            priceSelect.addEventListener('change', (e) => {
                window.AURA_APP.currentFilters.price = e.target.value;
                applyFilters();
            });
        }

        if (bedsSelect) {
            bedsSelect.addEventListener('change', (e) => {
                window.AURA_APP.currentFilters.bedrooms = e.target.value;
                applyFilters();
            });
        }

        // Quick Tag Buttons
        quickTagBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                quickTagBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                window.AURA_APP.currentFilters.quickTag = btn.getAttribute('data-filter-type') || 'all';
                applyFilters();
            });
        });

        // Catalog Sorting Dropdown
        if (catalogSort) {
            catalogSort.addEventListener('change', (e) => {
                window.AURA_APP.sortOption = e.target.value;
                sortCatalogCards();
            });
        }

        // Reset Filters Logic
        const resetFilters = () => {
            window.AURA_APP.currentFilters = {
                keyword: '',
                quickTag: 'all',
                transaction: 'all',
                location: 'all',
                category: 'all',
                price: 'all',
                bedrooms: 'all'
            };

            if (keywordInput) keywordInput.value = '';
            if (txSelect) txSelect.value = 'all';
            if (locSelect) locSelect.value = 'all';
            if (catSelect) catSelect.value = 'all';
            if (priceSelect) priceSelect.value = 'all';
            if (bedsSelect) bedsSelect.value = 'all';

            quickTagBtns.forEach(b => {
                if (b.getAttribute('data-filter-type') === 'all') {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });

            applyFilters();
            if (window.showToast) {
                window.showToast('Les filtres de recherche ont été réinitialisés.', 'info');
            }
        };

        if (resetBtn) resetBtn.addEventListener('click', resetFilters);
        resetAllBtns.forEach(btn => btn.addEventListener('click', resetFilters));

        // Read URL Query Params if navigating from homepage search form
        if (typeof window !== 'undefined' && window.location && window.location.search) {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('type')) {
                const type = urlParams.get('type');
                if (txSelect && type) {
                    txSelect.value = type;
                    window.AURA_APP.currentFilters.transaction = type;
                }
            }
            if (urlParams.has('location')) {
                const loc = urlParams.get('location');
                if (locSelect && loc) {
                    locSelect.value = loc;
                    window.AURA_APP.currentFilters.location = loc;
                }
            }
            if (urlParams.has('category')) {
                const cat = urlParams.get('category');
                if (catSelect && cat) {
                    catSelect.value = cat;
                    window.AURA_APP.currentFilters.category = cat;
                }
            }
        }

        applyFilters();
    },

    /* ==========================================================================
       8. FAQ INTERACTIVE LIVE SEARCH & CATEGORY FILTER (faq.html)
       ========================================================================== */
    initFaqInteractive() {
        if (typeof document === 'undefined') return;
        const searchInput = document.getElementById('faqSearchInput');
        const tabBtns = document.querySelectorAll('.faq-tab-btn');
        const groupBlocks = document.querySelectorAll('.faq-group-block');
        const noMatchCard = document.getElementById('faqNoMatchCard');
        const resetBtn = document.getElementById('resetFaqSearchBtn');

        if (!searchInput && tabBtns.length === 0) return; // Not on FAQ page

        let activeCategory = 'all';
        let searchQuery = '';

        const filterFaqItems = () => {
            let totalVisible = 0;

            groupBlocks.forEach(block => {
                const blockCat = block.getAttribute('data-category');
                const accordionItems = block.querySelectorAll('.faq-accordion-item');
                let blockVisibleCount = 0;

                // Category Check
                const categoryMatches = (activeCategory === 'all' || activeCategory === blockCat);

                accordionItems.forEach(item => {
                    const question = item.querySelector('.question-text')?.textContent.toLowerCase() || '';
                    const answer = item.querySelector('.faq-answer-content')?.textContent.toLowerCase() || '';
                    const fullText = `${question} ${answer}`;

                    let searchMatches = true;
                    if (searchQuery.trim() !== '') {
                        searchMatches = fullText.includes(searchQuery.toLowerCase().trim());
                    }

                    if (categoryMatches && searchMatches) {
                        item.classList.remove('hidden');
                        if (searchQuery.trim() !== '') {
                            item.setAttribute('open', 'true');
                        }
                        blockVisibleCount++;
                    } else {
                        item.classList.add('hidden');
                    }
                });

                if (blockVisibleCount > 0) {
                    block.classList.remove('hidden');
                    totalVisible += blockVisibleCount;
                } else {
                    block.classList.add('hidden');
                }
            });

            if (noMatchCard) {
                if (totalVisible === 0) {
                    noMatchCard.classList.remove('hidden');
                } else {
                    noMatchCard.classList.add('hidden');
                }
            }
        };

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                searchQuery = e.target.value;
                filterFaqItems();
            });
        }

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeCategory = btn.getAttribute('data-faq-cat') || 'all';
                filterFaqItems();
            });
        });

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                searchQuery = '';
                activeCategory = 'all';
                tabBtns.forEach(b => {
                    if (b.getAttribute('data-faq-cat') === 'all') b.classList.add('active');
                    else b.classList.remove('active');
                });
                filterFaqItems();
            });
        }
    },

    /* ==========================================================================
       9. INTERACTIVE MAP PINS & OFFICE SELECTOR SYNC (contact.html)
       ========================================================================== */
    initContactMapAndOffices() {
        if (typeof document === 'undefined') return;
        const mapPins = document.querySelectorAll('.map-pin');
        const switchBtns = document.querySelectorAll('.map-switch-btn');
        const coordsDisplay = document.getElementById('mapCoordsDisplay');
        const selectOfficeBtns = document.querySelectorAll('.select-office-btn');
        const officeSelectField = document.getElementById('contact-office');

        if (mapPins.length === 0 && switchBtns.length === 0) return;

        const coordinatesData = {
            'paris': 'GPS : 48.8661° N, 2.3082° E • 12 Avenue Montaigne',
            'monaco': 'GPS : 43.7384° N, 7.4246° E • 1 Place du Casino',
            'geneva': 'GPS : 46.2044° N, 6.1432° E • Rue du Rhône 42',
            'dubai': 'GPS : 25.2048° N, 55.2708° E • DIFC Gate Village 04'
        };

        const setActiveOffice = (officeKey) => {
            mapPins.forEach(pin => {
                if (pin.getAttribute('data-office') === officeKey) {
                    pin.classList.add('active');
                } else {
                    pin.classList.remove('active');
                }
            });

            switchBtns.forEach(btn => {
                if (btn.getAttribute('data-target') === officeKey) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            if (coordsDisplay && coordinatesData[officeKey]) {
                coordsDisplay.innerHTML = `<span>${coordinatesData[officeKey]}</span> <span class="divider">•</span> <span class="accent-gold">Accès Voiturier Réglé</span>`;
            }
        };

        mapPins.forEach(pin => {
            pin.addEventListener('click', () => {
                const office = pin.getAttribute('data-office');
                if (office) setActiveOffice(office);
            });
        });

        switchBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.getAttribute('data-target');
                if (target) setActiveOffice(target);
            });
        });

        // Select Office from cards to pre-fill form
        selectOfficeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const officeName = btn.getAttribute('data-office-name');
                if (officeSelectField && officeName) {
                    const lower = officeName.toLowerCase();
                    if (lower.includes('paris')) officeSelectField.value = 'paris';
                    else if (lower.includes('monaco')) officeSelectField.value = 'monaco';
                    else if (lower.includes('genève') || lower.includes('geneva')) officeSelectField.value = 'geneva';
                    else if (lower.includes('dubaï') || lower.includes('dubai')) officeSelectField.value = 'dubai';

                    const formContainer = document.querySelector('.contact-form-container');
                    if (formContainer) {
                        formContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }

                    if (window.showToast) {
                        window.showToast(`Bureau Référent ${officeName} sélectionné dans le formulaire.`, 'success');
                    }
                }
            });
        });
    },

    /* ==========================================================================
       10. FORM VALIDATION & CONFIDENTIAL LEAD CAPTURE
       ========================================================================== */
    initFormHandlers() {
        if (typeof document === 'undefined') return;
        // Valuation Form on Homepage
        const valuationForm = document.getElementById('valuationForm');
        if (valuationForm) {
            valuationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const fullname = document.getElementById('val-fullname')?.value || '';
                const email = document.getElementById('val-email')?.value || '';

                if (!fullname || !email) {
                    if (window.showToast) window.showToast('Veuillez remplir les champs obligatoires.', 'error');
                    return;
                }

                if (window.showToast) {
                    window.showToast('Votre demande d\'estimation confidentielle a été transmise. Un Directeur Associé vous recontactera sous 48h.', 'success', 6000);
                }

                valuationForm.reset();
            });
        }

        // Contact VIP Form on contact.html
        const contactForm = document.getElementById('contactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const fname = document.getElementById('contact-firstname')?.value || '';
                const lname = document.getElementById('contact-lastname')?.value || '';
                const email = document.getElementById('contact-email')?.value || '';

                if (!fname || !lname || !email) {
                    if (window.showToast) window.showToast('Veuillez renseigner vos coordonnées complètes.', 'error');
                    return;
                }

                if (window.showToast) {
                    window.showToast('Votre demande de rendez-vous privé est enregistrée sous accord NDA. Notre secrétariat vous recontacte sous 2h.', 'success', 6000);
                }

                contactForm.reset();
            });
        }
    },

    /* ==========================================================================
       11. SMOOTH SCROLL & REVEAL ANIMATIONS (IntersectionObserver)
       ========================================================================== */
    initScrollReveal() {
        if (typeof document === 'undefined' || typeof IntersectionObserver === 'undefined') return;
        const revealTargets = document.querySelectorAll(
            '.property-card, .service-preview-item, .stat-card, .valuation-card, .location-card, .step-card, .hub-card, .faq-accordion-item'
        );

        if (revealTargets.length === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-up');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -40px 0px'
        });

        revealTargets.forEach(el => observer.observe(el));
    }
};