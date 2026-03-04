/**
 * Elementor Price Simulator — Script principal (Vanilla JS)
 * Reproduit fidèlement la logique de offresgifteov1.netlify.app
 */
(function () {
    'use strict';

    // -------------------------------------------------------------------------
    // Moteur de tarification (identique à la page originale)
    // -------------------------------------------------------------------------
    function getPricing(count, cfg) {
        var max = cfg.sliderMax || 50;

        if (!count || count < 1)        return { isEmpty: true };
        if (count > max)                return { isCustom: true };

        var plans = cfg.plans;
        var result = { isFlat: false, plans: {} };

        if (count === 1) {
            result.isFlat = true;
            plans.forEach(function (p) {
                var pr = p.pricing;
                if (pr.flat1Mo || pr.flat1Yr) {
                    result.plans[p.id] = { mo: pr.flat1Mo, yr: pr.flat1Yr };
                } else {
                    result.plans[p.id] = null; // indisponible
                }
            });
            return result;
        }

        if (count >= 2 && count <= 4) {
            result.isFlat = true;
            plans.forEach(function (p) {
                var pr = p.pricing;
                if (pr.flat24Mo || pr.flat24Yr) {
                    result.plans[p.id] = { mo: pr.flat24Mo, yr: pr.flat24Yr };
                } else {
                    result.plans[p.id] = null;
                }
            });
            return result;
        }

        // Tranche par collaborateur
        plans.forEach(function (p) {
            var pr = p.pricing;
            var unit = 0;
            if      (count >= 5  && count <= 10) unit = pr.u5_10;
            else if (count >= 11 && count <= 20) unit = pr.u11_20;
            else if (count >= 21 && count <= 30) unit = pr.u21_30;
            else if (count >= 31 && count <= 40) unit = pr.u31_40;
            else if (count >= 41 && count <= max) unit = pr.u41_50;

            if (unit > 0) {
                result.plans[p.id] = {
                    mo:   unit * count,
                    yr:   unit * count * 12,
                    unit: unit,
                };
            } else {
                result.plans[p.id] = null;
            }
        });

        return result;
    }

    // -------------------------------------------------------------------------
    // Formateur de prix (style français)
    // -------------------------------------------------------------------------
    function formatPrice(value, currency) {
        if (value === null || value === undefined) return '—';
        var formatted = new Intl.NumberFormat('fr-FR', {
            minimumFractionDigits: value % 1 === 0 ? 0 : 2,
            maximumFractionDigits: 2,
        }).format(value);
        return formatted + '\u00a0' + (currency || '€');
    }

    // -------------------------------------------------------------------------
    // Multiplicateur final (engagement + fiscal)
    // -------------------------------------------------------------------------
    function getMultiplier(commitment, fiscalActive, fiscalDiscount) {
        var commitMult  = 1 - ((commitment - 2) * 0.05);
        var fiscalMult  = fiscalActive ? (1 - (fiscalDiscount / 100)) : 1;
        return commitMult * fiscalMult;
    }

    // -------------------------------------------------------------------------
    // Mise à jour du slider
    // -------------------------------------------------------------------------
    function updateSlider(wid, count, cfg) {
        var max      = (cfg.sliderMax || 50) + 1;
        var clamped  = Math.min(max, Math.max(1, count || 1));
        var pct      = ((clamped - 1) / (max - 1)) * 100;

        var fill  = document.getElementById(wid + '-fill');
        var thumb = document.getElementById(wid + '-thumb');
        var range = document.getElementById(wid + '-range');

        if (fill)  fill.style.width = pct + '%';
        if (thumb) thumb.style.left  = pct + '%';
        if (range) range.value = clamped;
    }

    // -------------------------------------------------------------------------
    // Mise à jour des cartes
    // -------------------------------------------------------------------------
    function updateCards(wid, cfg, state) {
        var pricing    = getPricing(state.count, cfg);
        var multiplier = getMultiplier(state.commitment, state.fiscal, cfg.fiscalDiscount || 25);
        var hasDiscount = multiplier < 0.9999;

        cfg.plans.forEach(function (plan) {
            var card = document.querySelector(
                '#' + wid + ' .eps-card[data-plan="' + plan.id + '"]'
            );
            if (!card) return;

            var priceBlock  = card.querySelector('.eps-price-block');
            var priceOrig   = card.querySelector('.eps-price-original');
            var priceStrike = card.querySelector('.eps-price-strike');
            var discBadge   = card.querySelector('.eps-discount-badge');
            var priceVal    = card.querySelector('.eps-price-value');
            var pricePer    = card.querySelector('.eps-price-period');
            var priceSub    = card.querySelector('.eps-price-subtitle');
            var ctaBtn      = card.querySelector('.eps-cta-btn');

            // Nettoyer les classes état
            card.classList.remove('eps-card-unavailable', 'eps-card-custom');

            if (pricing.isEmpty) {
                priceVal.textContent = '—';
                pricePer.textContent = '';
                priceSub.textContent = '';
                if (priceOrig) priceOrig.style.display = 'none';
                return;
            }

            if (pricing.isCustom) {
                card.classList.add('eps-card-custom');
                priceVal.textContent = 'Sur mesure';
                priceVal.classList.remove('eps-discounted');
                pricePer.textContent = '';
                priceSub.textContent = 'Pour les grandes équipes';
                if (priceOrig) priceOrig.style.display = 'none';
                if (ctaBtn) {
                    ctaBtn.classList.add('eps-cta-custom');
                    ctaBtn.classList.remove('eps-cta-disabled');
                    ctaBtn.textContent = 'Contacter notre équipe';
                }
                return;
            }

            var data = pricing.plans[plan.id];

            if (!data) {
                // Indisponible pour ce nombre de collabs
                card.classList.add('eps-card-unavailable');
                priceVal.textContent = 'Indisponible';
                priceVal.classList.remove('eps-discounted');
                pricePer.textContent = '';
                priceSub.textContent = 'Pour ' + state.count + ' collaborateur(s)';
                if (priceOrig) priceOrig.style.display = 'none';
                if (ctaBtn) {
                    ctaBtn.classList.add('eps-cta-disabled');
                    ctaBtn.classList.remove('eps-cta-custom');
                }
                return;
            }

            // Prix de base (avant remise)
            var basePrice = state.isAnnual ? data.yr : data.mo;
            // Prix final (après remise)
            var finalPrice = Math.round(basePrice * multiplier * 100) / 100;

            // Animation
            priceVal.classList.add('eps-animate');
            setTimeout(function () { priceVal.classList.remove('eps-animate'); }, 300);

            // Prix barré
            if (hasDiscount && priceOrig) {
                priceOrig.style.display = 'flex';
                if (priceStrike) priceStrike.textContent = formatPrice(basePrice, cfg.currency);
                if (discBadge)   discBadge.textContent   = state.fiscal ? 'Coût réel' : 'Remisé';
            } else if (priceOrig) {
                priceOrig.style.display = 'none';
            }

            // Prix final
            priceVal.textContent = formatPrice(finalPrice, cfg.currency);
            priceVal.classList.toggle('eps-discounted', hasDiscount);
            pricePer.textContent = '/' + (state.isAnnual ? 'an' : 'mois');

            // Sous-titre
            if (pricing.isFlat) {
                priceSub.textContent = 'Forfait global';
            } else {
                var unitFinal = Math.round(data.unit * multiplier * 100) / 100;
                var baseUnit  = data.unit;
                var sub = '';
                if (hasDiscount) {
                    sub = formatPrice(baseUnit, cfg.currency) + ' → ';
                }
                sub += 'Soit ' + formatPrice(unitFinal, cfg.currency) + ' / collab / mois';
                priceSub.textContent = sub;
            }

            // Rétablir le CTA
            if (ctaBtn) {
                ctaBtn.classList.remove('eps-cta-custom', 'eps-cta-disabled');
            }
        });
    }

    // -------------------------------------------------------------------------
    // Init d'un widget
    // -------------------------------------------------------------------------
    function EPSInit(wid, cfg) {
        var wrap = document.getElementById(wid);
        if (!wrap) return;

        // État initial
        var state = {
            count:      35,
            isAnnual:   true,
            commitment: 2,
            fiscal:     false,
        };

        // --- Éléments DOM ---
        var rangeInput  = document.getElementById(wid + '-range');
        var countInput  = document.getElementById(wid + '-count');
        var billingBtns = wrap.querySelectorAll('#' + wid + '-billing .eps-pill');
        var commitBtns  = wrap.querySelectorAll('#' + wid + '-commitment .eps-pill');
        var fiscalBtn   = document.getElementById(wid + '-fiscal');
        var thumb       = document.getElementById(wid + '-thumb');

        function refresh() {
            updateSlider(wid, state.count, cfg);
            updateCards(wid, cfg, state);
        }

        // --- Slider ---
        if (rangeInput) {
            rangeInput.addEventListener('input', function () {
                state.count = parseInt(this.value, 10);
                if (countInput) countInput.value = state.count;
                refresh();
            });
            rangeInput.addEventListener('mouseover', function () {
                if (thumb) thumb.classList.add('eps-thumb-hover');
            });
            rangeInput.addEventListener('mouseleave', function () {
                if (thumb) thumb.classList.remove('eps-thumb-hover');
            });
        }

        // --- Input numérique ---
        if (countInput) {
            countInput.addEventListener('input', function () {
                var val = parseInt(this.value, 10);
                if (!isNaN(val)) {
                    state.count = Math.max(1, val);
                } else {
                    state.count = 0;
                }
                refresh();
            });
            countInput.addEventListener('blur', function () {
                if (!this.value || parseInt(this.value, 10) < 1) {
                    this.value = 1;
                    state.count = 1;
                    refresh();
                }
            });
        }

        // --- Billing toggle ---
        billingBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                state.isAnnual = (this.dataset.value === 'annual');
                billingBtns.forEach(function (b) { b.classList.remove('eps-pill-active'); });
                this.classList.add('eps-pill-active');
                refresh();
            });
        });

        // --- Engagement ---
        commitBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                state.commitment = parseInt(this.dataset.value, 10);
                commitBtns.forEach(function (b) { b.classList.remove('eps-pill-active'); });
                this.classList.add('eps-pill-active');
                refresh();
            });
        });

        // --- Toggle fiscal ---
        if (fiscalBtn) {
            fiscalBtn.addEventListener('click', function () {
                state.fiscal = !state.fiscal;
                this.setAttribute('aria-pressed', state.fiscal ? 'true' : 'false');
                // Changer la couleur du titre fiscal
                var fiscalTitle = wrap.querySelector('.eps-fiscal-title');
                if (fiscalTitle) {
                    fiscalTitle.style.color = state.fiscal
                        ? 'var(--eps-primary)'
                        : 'var(--eps-slate-700)';
                }
                refresh();
            });
        }

        // Rendu initial
        refresh();
    }

    // Exposer globalement
    window.EPSInit = EPSInit;

    // Notifier que le script est prêt (pour les widgets déjà rendus)
    document.dispatchEvent(new CustomEvent('eps:ready'));

    // Support Elementor Editor : re-init sur chaque rafraîchissement de widget
    if (window.elementorFrontend) {
        window.elementorFrontend.hooks.addAction(
            'frontend/element_ready/eps_price_simulator.default',
            function ($scope) {
                var wid = $scope.find('[id^="eps-"]').attr('id');
                // Le script inline dans le widget appellera EPSInit directement
            }
        );
    }
})();
