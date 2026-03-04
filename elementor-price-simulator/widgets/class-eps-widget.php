<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

use Elementor\Widget_Base;
use Elementor\Controls_Manager;
use Elementor\Group_Control_Typography;

/**
 * Widget Elementor : Simulateur de prix Gifteo
 */
class EPS_Widget extends Widget_Base {

    public function get_name() {
        return 'eps_price_simulator';
    }

    public function get_title() {
        return __( 'Simulateur de Prix', 'elementor-price-simulator' );
    }

    public function get_icon() {
        return 'eicon-price-table';
    }

    public function get_categories() {
        return [ 'general' ];
    }

    public function get_keywords() {
        return [ 'prix', 'simulateur', 'tarif', 'devis', 'price', 'simulator' ];
    }

    public function get_script_depends() {
        return [ 'eps-frontend' ];
    }

    public function get_style_depends() {
        return [ 'eps-frontend' ];
    }

    // -------------------------------------------------------------------------
    // CONTRÔLES ELEMENTOR
    // -------------------------------------------------------------------------
    protected function register_controls() {

        /* ===== SECTION : IDENTITÉ ===== */
        $this->start_controls_section( 'section_identity', [
            'label' => __( 'Identité & Textes', 'elementor-price-simulator' ),
            'tab'   => Controls_Manager::TAB_CONTENT,
        ] );

        $this->add_control( 'logo_url', [
            'label'       => __( 'URL du logo', 'elementor-price-simulator' ),
            'type'        => Controls_Manager::MEDIA,
            'default'     => [ 'url' => '' ],
            'description' => __( 'Laissez vide pour masquer le logo.', 'elementor-price-simulator' ),
        ] );

        $this->add_control( 'heading_title', [
            'label'   => __( 'Titre principal', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXT,
            'default' => __( 'Des tarifs simples pour vos équipes', 'elementor-price-simulator' ),
        ] );

        $this->add_control( 'heading_highlight', [
            'label'   => __( 'Mot(s) mis en couleur', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXT,
            'default' => __( 'vos équipes', 'elementor-price-simulator' ),
        ] );

        $this->add_control( 'heading_subtitle', [
            'label'   => __( 'Sous-titre', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXTAREA,
            'default' => __( 'Ajustez le curseur, choisissez votre engagement et découvrez le coût réel pour votre entreprise.', 'elementor-price-simulator' ),
        ] );

        $this->add_control( 'contact_text', [
            'label'   => __( 'Texte lien de contact', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXT,
            'default' => __( 'Vous avez un besoin spécifique ? Contactez notre équipe de vente.', 'elementor-price-simulator' ),
        ] );

        $this->add_control( 'contact_url', [
            'label'   => __( 'URL du lien de contact', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::URL,
            'default' => [ 'url' => '#contact' ],
        ] );

        $this->end_controls_section();

        /* ===== SECTION : TARIFICATION ===== */
        $this->start_controls_section( 'section_pricing', [
            'label' => __( 'Tarification', 'elementor-price-simulator' ),
            'tab'   => Controls_Manager::TAB_CONTENT,
        ] );

        $this->add_control( 'currency', [
            'label'   => __( 'Devise', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXT,
            'default' => '€',
        ] );

        $this->add_control( 'slider_max', [
            'label'   => __( 'Maximum collaborateurs (avant "Sur mesure")', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::NUMBER,
            'min'     => 10,
            'max'     => 500,
            'default' => 50,
        ] );

        $this->add_control( 'show_annual_toggle', [
            'label'        => __( 'Afficher le toggle Mensuel/Annuel', 'elementor-price-simulator' ),
            'type'         => Controls_Manager::SWITCHER,
            'label_on'     => __( 'Oui', 'elementor-price-simulator' ),
            'label_off'    => __( 'Non', 'elementor-price-simulator' ),
            'return_value' => 'yes',
            'default'      => 'yes',
        ] );

        $this->add_control( 'show_commitment', [
            'label'        => __( 'Afficher le sélecteur d\'engagement', 'elementor-price-simulator' ),
            'type'         => Controls_Manager::SWITCHER,
            'label_on'     => __( 'Oui', 'elementor-price-simulator' ),
            'label_off'    => __( 'Non', 'elementor-price-simulator' ),
            'return_value' => 'yes',
            'default'      => 'yes',
        ] );

        $this->add_control( 'show_fiscal', [
            'label'        => __( 'Afficher l\'avantage fiscal', 'elementor-price-simulator' ),
            'type'         => Controls_Manager::SWITCHER,
            'label_on'     => __( 'Oui', 'elementor-price-simulator' ),
            'label_off'    => __( 'Non', 'elementor-price-simulator' ),
            'return_value' => 'yes',
            'default'      => 'yes',
        ] );

        $this->add_control( 'fiscal_discount', [
            'label'      => __( 'Réduction avantage fiscal (%)', 'elementor-price-simulator' ),
            'type'       => Controls_Manager::NUMBER,
            'min'        => 1,
            'max'        => 100,
            'default'    => 25,
            'condition'  => [ 'show_fiscal' => 'yes' ],
        ] );

        $this->end_controls_section();

        /* ===== SECTION : OFFRE IMPULSION ===== */
        $this->_register_plan_section( 'impulsion', __( 'Offre Impulsion', 'elementor-price-simulator' ), [
            'flat_1_mo'   => 33.33,
            'flat_1_yr'   => 400,
            'flat_24_mo'  => 50,
            'flat_24_yr'  => 600,
            'u_5_10'      => 10,
            'u_11_20'     => 8,
            'u_21_30'     => 7,
            'u_31_40'     => 6,
            'u_41_50'     => 5,
        ] );

        /* ===== SECTION : OFFRE ESSENTIEL ===== */
        $this->_register_plan_section( 'essentiel', __( 'Offre Essentiel', 'elementor-price-simulator' ), [
            'flat_1_mo'   => null,
            'flat_1_yr'   => null,
            'flat_24_mo'  => 58.33,
            'flat_24_yr'  => 700,
            'u_5_10'      => 12.5,
            'u_11_20'     => 10,
            'u_21_30'     => 8.5,
            'u_31_40'     => 7,
            'u_41_50'     => 6,
        ], true );

        /* ===== SECTION : OFFRE PERFORMANCE ===== */
        $this->_register_plan_section( 'performance', __( 'Offre Performance', 'elementor-price-simulator' ), [
            'flat_1_mo'   => null,
            'flat_1_yr'   => null,
            'flat_24_mo'  => 75,
            'flat_24_yr'  => 900,
            'u_5_10'      => 20,
            'u_11_20'     => 16,
            'u_21_30'     => 14,
            'u_31_40'     => 12,
            'u_41_50'     => 11,
        ] );

        /* ===== SECTION : STYLE ===== */
        $this->start_controls_section( 'section_style', [
            'label' => __( 'Style & Couleurs', 'elementor-price-simulator' ),
            'tab'   => Controls_Manager::TAB_STYLE,
        ] );

        $this->add_control( 'primary_color', [
            'label'   => __( 'Couleur principale', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::COLOR,
            'default' => '#f97316',
        ] );

        $this->add_control( 'secondary_color', [
            'label'   => __( 'Couleur secondaire', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::COLOR,
            'default' => '#ef4444',
        ] );

        $this->add_control( 'show_animated_bg', [
            'label'        => __( 'Fond animé (mesh gradient)', 'elementor-price-simulator' ),
            'type'         => Controls_Manager::SWITCHER,
            'label_on'     => __( 'Oui', 'elementor-price-simulator' ),
            'label_off'    => __( 'Non', 'elementor-price-simulator' ),
            'return_value' => 'yes',
            'default'      => 'yes',
        ] );

        $this->end_controls_section();
    }

    /**
     * Enregistre les contrôles Elementor d'un plan tarifaire.
     */
    private function _register_plan_section( $plan_id, $label, $defaults, $popular = false ) {
        $this->start_controls_section( 'section_plan_' . $plan_id, [
            'label' => $label,
            'tab'   => Controls_Manager::TAB_CONTENT,
        ] );

        $this->add_control( $plan_id . '_name', [
            'label'   => __( 'Nom de l\'offre', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXT,
            'default' => ucfirst( $plan_id ),
        ] );

        $this->add_control( $plan_id . '_popular', [
            'label'        => __( '"Le plus choisi"', 'elementor-price-simulator' ),
            'type'         => Controls_Manager::SWITCHER,
            'return_value' => 'yes',
            'default'      => $popular ? 'yes' : '',
        ] );

        $this->add_control( $plan_id . '_cta', [
            'label'   => __( 'Texte du bouton', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::TEXT,
            'default' => __( 'Commencer', 'elementor-price-simulator' ),
        ] );

        $this->add_control( $plan_id . '_cta_url', [
            'label'   => __( 'URL du bouton', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::URL,
            'default' => [ 'url' => '#' ],
        ] );

        // Fonctionnalités
        $this->add_control( $plan_id . '_features', [
            'label'       => __( 'Fonctionnalités (une par ligne, préfixe ✓ ou ✗)', 'elementor-price-simulator' ),
            'type'        => Controls_Manager::TEXTAREA,
            'default'     => $this->_default_features( $plan_id ),
            'description' => __( 'Commencez chaque ligne par ✓ ou ✗ selon l\'inclusion.', 'elementor-price-simulator' ),
        ] );

        // Tarifs forfait 1 salarié
        $this->add_control( $plan_id . '_heading_flat1', [
            'label' => __( 'Tarifs forfait (1 collab.)', 'elementor-price-simulator' ),
            'type'  => Controls_Manager::HEADING,
            'separator' => 'before',
        ] );
        $this->add_control( $plan_id . '_flat_1_mo', [
            'label'   => __( 'Mensuel (€)', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::NUMBER,
            'default' => $defaults['flat_1_mo'],
        ] );
        $this->add_control( $plan_id . '_flat_1_yr', [
            'label'   => __( 'Annuel (€)', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::NUMBER,
            'default' => $defaults['flat_1_yr'],
        ] );

        // Tarifs forfait 2-4 salariés
        $this->add_control( $plan_id . '_heading_flat24', [
            'label' => __( 'Tarifs forfait (2–4 collabs)', 'elementor-price-simulator' ),
            'type'  => Controls_Manager::HEADING,
            'separator' => 'before',
        ] );
        $this->add_control( $plan_id . '_flat_24_mo', [
            'label'   => __( 'Mensuel (€)', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::NUMBER,
            'default' => $defaults['flat_24_mo'],
        ] );
        $this->add_control( $plan_id . '_flat_24_yr', [
            'label'   => __( 'Annuel (€)', 'elementor-price-simulator' ),
            'type'    => Controls_Manager::NUMBER,
            'default' => $defaults['flat_24_yr'],
        ] );

        // Tarifs par collaborateur selon tranches
        $tranches = [
            '5_10'  => '5–10',
            '11_20' => '11–20',
            '21_30' => '21–30',
            '31_40' => '31–40',
            '41_50' => '41–50',
        ];
        foreach ( $tranches as $key => $range ) {
            $this->add_control( $plan_id . '_heading_u_' . $key, [
                'label'     => sprintf( __( 'Prix / collab / mois — %s collabs', 'elementor-price-simulator' ), $range ),
                'type'      => Controls_Manager::HEADING,
                'separator' => 'before',
            ] );
            $this->add_control( $plan_id . '_u_' . $key, [
                'label'   => __( 'Prix unitaire (€)', 'elementor-price-simulator' ),
                'type'    => Controls_Manager::NUMBER,
                'default' => $defaults[ 'u_' . $key ],
            ] );
        }

        $this->end_controls_section();
    }

    private function _default_features( $plan ) {
        $map = [
            'impulsion'   => "✓ Accès au catalogue cadeaux\n✓ Support par email\n✗ Account Manager dédié\n✗ App sur mesure & Accès VIP",
            'essentiel'   => "✓ Accès au catalogue cadeaux\n✓ Support par email\n✓ Account Manager dédié\n✗ App sur mesure & Accès VIP",
            'performance' => "✓ Accès au catalogue cadeaux\n✓ Support par email\n✓ Account Manager dédié\n✓ Application sur mesure & Accès VIP",
        ];
        return isset( $map[ $plan ] ) ? $map[ $plan ] : '';
    }

    // -------------------------------------------------------------------------
    // RENDU HTML
    // -------------------------------------------------------------------------
    protected function render() {
        $s = $this->get_settings_for_display();

        // Construire la config JSON transmise au JS
        $config = [
            'currency'      => esc_attr( $s['currency'] ?? '€' ),
            'sliderMax'     => intval( $s['slider_max'] ?? 50 ),
            'showAnnual'    => ( $s['show_annual_toggle'] ?? 'yes' ) === 'yes',
            'showCommitment'=> ( $s['show_commitment']  ?? 'yes' ) === 'yes',
            'showFiscal'    => ( $s['show_fiscal']      ?? 'yes' ) === 'yes',
            'fiscalDiscount'=> intval( $s['fiscal_discount'] ?? 25 ),
            'plans'         => [],
        ];

        $plan_ids = [ 'impulsion', 'essentiel', 'performance' ];
        foreach ( $plan_ids as $pid ) {
            $features_raw = $s[ $pid . '_features' ] ?? '';
            $features     = $this->_parse_features( $features_raw );

            $config['plans'][] = [
                'id'       => $pid,
                'name'     => esc_html( $s[ $pid . '_name' ] ?? ucfirst( $pid ) ),
                'popular'  => ( $s[ $pid . '_popular' ] ?? '' ) === 'yes',
                'cta'      => esc_html( $s[ $pid . '_cta' ] ?? __( 'Commencer', 'elementor-price-simulator' ) ),
                'ctaUrl'   => esc_url( $s[ $pid . '_cta_url' ]['url'] ?? '#' ),
                'features' => $features,
                'pricing'  => [
                    'flat1Mo'  => floatval( $s[ $pid . '_flat_1_mo' ]  ?? 0 ),
                    'flat1Yr'  => floatval( $s[ $pid . '_flat_1_yr' ]  ?? 0 ),
                    'flat24Mo' => floatval( $s[ $pid . '_flat_24_mo' ] ?? 0 ),
                    'flat24Yr' => floatval( $s[ $pid . '_flat_24_yr' ] ?? 0 ),
                    'u5_10'    => floatval( $s[ $pid . '_u_5_10' ]  ?? 0 ),
                    'u11_20'   => floatval( $s[ $pid . '_u_11_20' ] ?? 0 ),
                    'u21_30'   => floatval( $s[ $pid . '_u_21_30' ] ?? 0 ),
                    'u31_40'   => floatval( $s[ $pid . '_u_31_40' ] ?? 0 ),
                    'u41_50'   => floatval( $s[ $pid . '_u_41_50' ] ?? 0 ),
                ],
            ];
        }

        $logo_url      = ! empty( $s['logo_url']['url'] )  ? esc_url( $s['logo_url']['url'] ) : '';
        $title         = esc_html( $s['heading_title']    ?? '' );
        $highlight     = esc_html( $s['heading_highlight'] ?? '' );
        $subtitle      = esc_html( $s['heading_subtitle'] ?? '' );
        $contact_text  = esc_html( $s['contact_text']     ?? '' );
        $contact_url   = esc_url( $s['contact_url']['url'] ?? '#' );
        $primary_color = esc_attr( $s['primary_color']    ?? '#f97316' );
        $secondary_color = esc_attr( $s['secondary_color'] ?? '#ef4444' );
        $animated_bg   = ( $s['show_animated_bg'] ?? 'yes' ) === 'yes';

        // Titre avec mise en couleur du mot clé
        $title_html = $title;
        if ( $highlight && strpos( $title, $highlight ) !== false ) {
            $title_html = str_replace(
                $highlight,
                '<span class="eps-highlight">' . $highlight . '</span>',
                $title
            );
        }

        $widget_id = 'eps-' . $this->get_id();
        ?>
        <style>
            #<?php echo $widget_id; ?> {
                --eps-primary: <?php echo $primary_color; ?>;
                --eps-secondary: <?php echo $secondary_color; ?>;
                --eps-gradient: linear-gradient(135deg, <?php echo $primary_color; ?>, <?php echo $secondary_color; ?>);
            }
        </style>

        <div id="<?php echo esc_attr( $widget_id ); ?>" class="eps-wrap <?php echo $animated_bg ? 'eps-animated-bg' : ''; ?>">

            <?php if ( $animated_bg ) : ?>
            <div class="eps-mesh-bg" aria-hidden="true">
                <div class="eps-blob eps-blob-1"></div>
                <div class="eps-blob eps-blob-2"></div>
                <div class="eps-blob eps-blob-3"></div>
            </div>
            <?php endif; ?>

            <div class="eps-inner">

                <?php if ( $logo_url ) : ?>
                <div class="eps-logo-wrap">
                    <img src="<?php echo $logo_url; ?>" alt="Logo" class="eps-logo" />
                </div>
                <?php endif; ?>

                <!-- En-tête -->
                <div class="eps-header">
                    <h2 class="eps-title"><?php echo $title_html; ?></h2>
                    <?php if ( $subtitle ) : ?>
                    <p class="eps-subtitle"><?php echo $subtitle; ?></p>
                    <?php endif; ?>
                </div>

                <!-- Panneau de contrôle -->
                <div class="eps-controls-panel">

                    <!-- Slider effectif -->
                    <div class="eps-control-row eps-slider-row">
                        <div class="eps-slider-header">
                            <span class="eps-label">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                                Effectif de l'entreprise
                            </span>
                            <input type="number" class="eps-count-input" id="<?php echo esc_attr( $widget_id ); ?>-count" value="35" min="1" max="999" />
                        </div>
                        <div class="eps-slider-track-wrap">
                            <div class="eps-slider-track">
                                <div class="eps-slider-fill" id="<?php echo esc_attr( $widget_id ); ?>-fill"></div>
                            </div>
                            <div class="eps-slider-thumb" id="<?php echo esc_attr( $widget_id ); ?>-thumb"></div>
                            <input type="range" class="eps-range" id="<?php echo esc_attr( $widget_id ); ?>-range"
                                min="1" max="<?php echo intval( $s['slider_max'] ?? 50 ) + 1; ?>" value="35" />
                        </div>
                        <div class="eps-slider-labels">
                            <span>1</span><span>10</span><span>20</span><span>30</span><span>40</span><span>50</span><span>51+</span>
                        </div>
                    </div>

                    <hr class="eps-divider" />

                    <!-- Options -->
                    <div class="eps-options-row">

                        <?php if ( ( $s['show_annual_toggle'] ?? 'yes' ) === 'yes' ) : ?>
                        <!-- Rythme de facturation -->
                        <div class="eps-option-group">
                            <label class="eps-option-label">Rythme de facturation</label>
                            <div class="eps-pill-group" id="<?php echo esc_attr( $widget_id ); ?>-billing">
                                <button class="eps-pill" data-value="monthly">Mensuel</button>
                                <button class="eps-pill eps-pill-active" data-value="annual">Annuel</button>
                            </div>
                        </div>
                        <?php endif; ?>

                        <?php if ( ( $s['show_commitment'] ?? 'yes' ) === 'yes' ) : ?>
                        <!-- Engagement -->
                        <div class="eps-option-group">
                            <label class="eps-option-label">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                                Années d'engagement
                            </label>
                            <div class="eps-pill-group eps-commitment-group" id="<?php echo esc_attr( $widget_id ); ?>-commitment">
                                <button class="eps-pill eps-pill-active" data-value="2" data-discount="0">2 ans</button>
                                <button class="eps-pill" data-value="3" data-discount="5"><span>3 ans</span><em>-5%</em></button>
                                <button class="eps-pill" data-value="4" data-discount="10"><span>4 ans</span><em>-10%</em></button>
                                <button class="eps-pill" data-value="5" data-discount="15"><span>5 ans</span><em>-15%</em></button>
                            </div>
                        </div>
                        <?php endif; ?>

                        <?php if ( ( $s['show_fiscal'] ?? 'yes' ) === 'yes' ) : ?>
                        <!-- Avantage fiscal -->
                        <div class="eps-option-group">
                            <label class="eps-option-label">Avantage Fiscal (IS)</label>
                            <div class="eps-fiscal-row">
                                <button class="eps-toggle" id="<?php echo esc_attr( $widget_id ); ?>-fiscal" aria-pressed="false">
                                    <span class="eps-toggle-thumb"></span>
                                </button>
                                <div class="eps-fiscal-desc">
                                    <span class="eps-fiscal-title">Compte 604</span>
                                    <span class="eps-fiscal-sub">Voir le coût réel (-<?php echo intval( $s['fiscal_discount'] ?? 25 ); ?>%)</span>
                                </div>
                            </div>
                        </div>
                        <?php endif; ?>

                    </div>
                </div><!-- /.eps-controls-panel -->

                <!-- Cartes tarifaires -->
                <div class="eps-cards" id="<?php echo esc_attr( $widget_id ); ?>-cards">
                    <?php foreach ( $config['plans'] as $plan ) : ?>
                    <div class="eps-card <?php echo $plan['popular'] ? 'eps-card-popular' : ''; ?>"
                         data-plan="<?php echo esc_attr( $plan['id'] ); ?>">

                        <?php if ( $plan['popular'] ) : ?>
                        <div class="eps-popular-badge">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                            Le plus choisi
                        </div>
                        <?php endif; ?>

                        <div class="eps-card-header">
                            <h3 class="eps-plan-name"><?php echo esc_html( $plan['name'] ); ?></h3>
                        </div>

                        <div class="eps-price-block" data-plan-id="<?php echo esc_attr( $plan['id'] ); ?>">
                            <div class="eps-price-original" style="display:none;">
                                <span class="eps-price-strike"></span>
                                <span class="eps-discount-badge"></span>
                            </div>
                            <div class="eps-price-main">
                                <span class="eps-price-value">—</span>
                                <span class="eps-price-period"></span>
                            </div>
                            <p class="eps-price-subtitle"></p>
                        </div>

                        <ul class="eps-features">
                            <?php foreach ( $plan['features'] as $feature ) : ?>
                            <li class="eps-feature <?php echo $feature['included'] ? 'eps-feature-yes' : 'eps-feature-no'; ?>">
                                <?php if ( $feature['included'] ) : ?>
                                <span class="eps-feature-icon eps-icon-yes">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                                </span>
                                <?php else : ?>
                                <span class="eps-feature-icon eps-icon-no">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                                </span>
                                <?php endif; ?>
                                <?php echo esc_html( $feature['text'] ); ?>
                            </li>
                            <?php endforeach; ?>
                        </ul>

                        <a href="<?php echo esc_url( $plan['ctaUrl'] ); ?>" class="eps-cta-btn">
                            <?php echo esc_html( $plan['cta'] ); ?>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                        </a>
                    </div>
                    <?php endforeach; ?>
                </div><!-- /.eps-cards -->

                <!-- Note légale -->
                <div class="eps-legal">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    <div>
                        <p><strong>Tous les prix sont affichés en Euros (€) hors taxes (HT).</strong></p>
                        <p>* En activant l'<strong>Avantage Fiscal</strong>, le tarif affiché correspond au "coût de revient réel" pour votre entreprise. Les prestations sont à inscrire sur le <strong>compte 604</strong>, permettant de les déduire du résultat imposable (économie IS estimée au taux standard de <?php echo intval( $s['fiscal_discount'] ?? 25 ); ?>%).</p>
                    </div>
                </div>

                <?php if ( $contact_text ) : ?>
                <div class="eps-footer-contact">
                    <?php
                    // Wrap "Contactez notre équipe de vente" in a link
                    $contact_linked = preg_replace(
                        '/(Contactez[^.]*)/i',
                        '<a href="' . $contact_url . '" class="eps-contact-link">$1</a>',
                        $contact_text
                    );
                    echo $contact_linked;
                    ?>
                </div>
                <?php endif; ?>

            </div><!-- /.eps-inner -->
        </div><!-- /.eps-wrap -->

        <script>
        (function() {
            var cfg = <?php echo wp_json_encode( $config ); ?>;
            var wid = <?php echo wp_json_encode( $widget_id ); ?>;
            if (window.EPSInit) { window.EPSInit(wid, cfg); }
            else { document.addEventListener('eps:ready', function() { window.EPSInit(wid, cfg); }); }
        })();
        </script>
        <?php
    }

    private function _parse_features( $raw ) {
        $lines    = array_filter( array_map( 'trim', explode( "\n", $raw ) ) );
        $features = [];
        foreach ( $lines as $line ) {
            $included = ( substr( $line, 0, 1 ) === '✓' || substr( $line, 0, 3 ) === '✓' );
            $text     = trim( preg_replace( '/^[✓✗]\s*/', '', $line ) );
            $features[] = [ 'text' => $text, 'included' => $included ];
        }
        return $features;
    }
}
