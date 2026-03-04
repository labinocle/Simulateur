<?php
/**
 * Plugin Name: Elementor Price Simulator
 * Plugin URI:  https://github.com/labinocle/Simulateur
 * Description: Widget Elementor pour simuler et afficher un prix dynamique basé sur un formulaire configurable.
 * Version:     1.0.0
 * Author:      labinocle
 * Text Domain: elementor-price-simulator
 * Domain Path: /languages
 * Requires at least: 5.8
 * Requires PHP: 7.4
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

define( 'EPS_VERSION', '1.0.0' );
define( 'EPS_FILE', __FILE__ );
define( 'EPS_PATH', plugin_dir_path( __FILE__ ) );
define( 'EPS_URL', plugin_dir_url( __FILE__ ) );
define( 'EPS_OPTION_KEY', 'eps_simulator_config' );

/**
 * Classe principale du plugin
 */
final class Elementor_Price_Simulator {

    private static $instance = null;

    public static function instance() {
        if ( is_null( self::$instance ) ) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action( 'plugins_loaded', [ $this, 'init' ] );
    }

    public function init() {
        // Vérifier qu'Elementor est actif
        if ( ! did_action( 'elementor/loaded' ) ) {
            add_action( 'admin_notices', [ $this, 'admin_notice_missing_elementor' ] );
            return;
        }

        $this->includes();
        $this->hooks();
    }

    private function includes() {
        require_once EPS_PATH . 'includes/class-eps-config.php';
        require_once EPS_PATH . 'includes/class-eps-calculator.php';
        require_once EPS_PATH . 'admin/class-eps-admin.php';
        require_once EPS_PATH . 'widgets/class-eps-widget.php';
    }

    private function hooks() {
        add_action( 'elementor/widgets/register', [ $this, 'register_widgets' ] );
        add_action( 'elementor/frontend/after_enqueue_styles', [ $this, 'enqueue_frontend_styles' ] );
        add_action( 'elementor/frontend/after_enqueue_scripts', [ $this, 'enqueue_frontend_scripts' ] );
        add_action( 'wp_ajax_eps_get_price', [ $this, 'ajax_get_price' ] );
        add_action( 'wp_ajax_nopriv_eps_get_price', [ $this, 'ajax_get_price' ] );
    }

    public function register_widgets( $widgets_manager ) {
        $widgets_manager->register( new EPS_Widget() );
    }

    public function enqueue_frontend_styles() {
        wp_enqueue_style(
            'eps-frontend',
            EPS_URL . 'assets/css/price-simulator.css',
            [],
            EPS_VERSION
        );
    }

    public function enqueue_frontend_scripts() {
        wp_enqueue_script(
            'eps-frontend',
            EPS_URL . 'assets/js/price-simulator.js',
            [ 'jquery' ],
            EPS_VERSION,
            true
        );

        wp_localize_script( 'eps-frontend', 'epsConfig', [
            'ajaxUrl' => admin_url( 'admin-ajax.php' ),
            'nonce'   => wp_create_nonce( 'eps_nonce' ),
        ] );
    }

    public function ajax_get_price() {
        check_ajax_referer( 'eps_nonce', 'nonce' );

        $form_data   = isset( $_POST['form_data'] ) ? (array) $_POST['form_data'] : [];
        $config_id   = isset( $_POST['config_id'] ) ? sanitize_text_field( $_POST['config_id'] ) : '';

        $config     = EPS_Config::get( $config_id );
        $calculator = new EPS_Calculator( $config );
        $result     = $calculator->calculate( $form_data );

        wp_send_json_success( $result );
    }

    public function admin_notice_missing_elementor() {
        $message = sprintf(
            /* translators: %s: Plugin name */
            esc_html__( '"%s" nécessite que le plugin Elementor soit installé et activé.', 'elementor-price-simulator' ),
            '<strong>Elementor Price Simulator</strong>'
        );
        printf( '<div class="notice notice-warning is-dismissible"><p>%s</p></div>', $message );
    }
}

// Activation / Désactivation
register_activation_hook( __FILE__, 'eps_activate' );
register_deactivation_hook( __FILE__, 'eps_deactivate' );

function eps_activate() {
    // Ajouter une configuration de démonstration si aucune n'existe
    if ( ! get_option( EPS_OPTION_KEY ) ) {
        $demo_config = [
            'demo' => [
                'label'      => 'Simulateur Demo',
                'base_price' => 100,
                'currency'   => '€',
                'fields'     => [
                    [
                        'id'      => 'surface',
                        'label'   => 'Surface (m²)',
                        'type'    => 'number',
                        'min'     => 10,
                        'max'     => 500,
                        'default' => 50,
                        'price_rule' => [
                            'type'  => 'multiply',
                            'value' => 2,
                        ],
                    ],
                    [
                        'id'      => 'type_travaux',
                        'label'   => 'Type de travaux',
                        'type'    => 'select',
                        'options' => [
                            [ 'value' => 'standard',  'label' => 'Standard',  'price' => 0 ],
                            [ 'value' => 'premium',   'label' => 'Premium',   'price' => 500 ],
                            [ 'value' => 'luxe',      'label' => 'Luxe',      'price' => 1500 ],
                        ],
                        'default' => 'standard',
                    ],
                    [
                        'id'      => 'options',
                        'label'   => 'Options supplémentaires',
                        'type'    => 'checkbox_group',
                        'options' => [
                            [ 'value' => 'peinture',    'label' => 'Peinture',      'price' => 200 ],
                            [ 'value' => 'electricite', 'label' => 'Électricité',   'price' => 350 ],
                            [ 'value' => 'plomberie',   'label' => 'Plomberie',     'price' => 400 ],
                        ],
                    ],
                    [
                        'id'      => 'urgence',
                        'label'   => 'Intervention urgente (+20%)',
                        'type'    => 'toggle',
                        'price_rule' => [
                            'type'    => 'percent',
                            'value'   => 20,
                        ],
                        'default' => false,
                    ],
                ],
            ],
        ];
        update_option( EPS_OPTION_KEY, $demo_config );
    }
}

function eps_deactivate() {
    // Nettoyage si nécessaire
}

// Lancer le plugin
Elementor_Price_Simulator::instance();
