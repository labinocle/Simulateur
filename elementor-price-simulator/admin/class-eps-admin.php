<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Page d'administration du plugin
 * (Gestion des configurations de simulateur sauvegardées en base)
 */
class EPS_Admin {

    public function __construct() {
        add_action( 'admin_menu',            [ $this, 'add_menu' ] );
        add_action( 'admin_enqueue_scripts', [ $this, 'enqueue_admin_assets' ] );
        add_action( 'admin_init',            [ $this, 'handle_save' ] );
        add_action( 'admin_init',            [ $this, 'handle_delete' ] );
        add_action( 'admin_notices',         [ $this, 'admin_notices' ] );
    }

    public function add_menu() {
        add_options_page(
            __( 'Simulateur de Prix', 'elementor-price-simulator' ),
            __( 'Simulateur Prix', 'elementor-price-simulator' ),
            'manage_options',
            'eps-settings',
            [ $this, 'render_page' ]
        );
    }

    public function enqueue_admin_assets( $hook ) {
        if ( $hook !== 'settings_page_eps-settings' ) {
            return;
        }
        wp_enqueue_style(
            'eps-admin',
            EPS_URL . 'admin/admin.css',
            [],
            EPS_VERSION
        );
    }

    public function handle_save() {
        if ( ! isset( $_POST['eps_action'] ) || $_POST['eps_action'] !== 'save_config' ) {
            return;
        }
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        check_admin_referer( 'eps_save_config' );

        $id = sanitize_key( $_POST['eps_config_id'] ?? '' );
        if ( empty( $id ) ) {
            $id = EPS_Config::generate_id( $_POST['eps_label'] ?? 'simulateur' );
        }

        $config = [
            'label'      => sanitize_text_field( $_POST['eps_label'] ?? '' ),
            'base_price' => floatval( $_POST['eps_base_price'] ?? 0 ),
            'currency'   => sanitize_text_field( $_POST['eps_currency'] ?? '€' ),
            'fields'     => [],
        ];

        // Les champs sont gérés via le widget Elementor, pas ici.
        // Cette page admin sert surtout à voir/supprimer les configs.

        EPS_Config::save( $id, $config );

        wp_safe_redirect( add_query_arg( [
            'page'    => 'eps-settings',
            'updated' => '1',
        ], admin_url( 'options-general.php' ) ) );
        exit;
    }

    public function handle_delete() {
        if ( ! isset( $_GET['eps_delete'] ) ) {
            return;
        }
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        check_admin_referer( 'eps_delete_' . $_GET['eps_delete'] );

        EPS_Config::delete( sanitize_key( $_GET['eps_delete'] ) );

        wp_safe_redirect( add_query_arg( [
            'page'    => 'eps-settings',
            'deleted' => '1',
        ], admin_url( 'options-general.php' ) ) );
        exit;
    }

    public function admin_notices() {
        $screen = get_current_screen();
        if ( ! $screen || $screen->id !== 'settings_page_eps-settings' ) {
            return;
        }
        if ( isset( $_GET['updated'] ) ) {
            echo '<div class="notice notice-success is-dismissible"><p>' .
                esc_html__( 'Configuration sauvegardée.', 'elementor-price-simulator' ) .
                '</p></div>';
        }
        if ( isset( $_GET['deleted'] ) ) {
            echo '<div class="notice notice-warning is-dismissible"><p>' .
                esc_html__( 'Configuration supprimée.', 'elementor-price-simulator' ) .
                '</p></div>';
        }
    }

    public function render_page() {
        $configs = EPS_Config::get_all();
        ?>
        <div class="wrap eps-admin-wrap">
            <h1 class="eps-admin-title">
                <span class="eps-admin-icon">💰</span>
                <?php esc_html_e( 'Simulateur de Prix — Administration', 'elementor-price-simulator' ); ?>
            </h1>

            <div class="eps-admin-grid">

                <!-- Liste des configs -->
                <div class="eps-admin-card">
                    <h2><?php esc_html_e( 'Configurations existantes', 'elementor-price-simulator' ); ?></h2>
                    <p class="eps-admin-desc">
                        <?php esc_html_e( 'Les paramètres détaillés de chaque simulateur (tarifs, offres, options) se configurent directement dans l\'éditeur Elementor via les contrôles du widget "Simulateur de Prix".', 'elementor-price-simulator' ); ?>
                    </p>

                    <?php if ( empty( $configs ) ) : ?>
                    <div class="eps-admin-empty">
                        <p><?php esc_html_e( 'Aucune configuration. Ajoutez le widget "Simulateur de Prix" dans Elementor pour commencer.', 'elementor-price-simulator' ); ?></p>
                    </div>
                    <?php else : ?>
                    <table class="wp-list-table widefat fixed striped eps-admin-table">
                        <thead>
                            <tr>
                                <th><?php esc_html_e( 'ID', 'elementor-price-simulator' ); ?></th>
                                <th><?php esc_html_e( 'Libellé', 'elementor-price-simulator' ); ?></th>
                                <th><?php esc_html_e( 'Prix de base', 'elementor-price-simulator' ); ?></th>
                                <th><?php esc_html_e( 'Devise', 'elementor-price-simulator' ); ?></th>
                                <th><?php esc_html_e( 'Actions', 'elementor-price-simulator' ); ?></th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ( $configs as $id => $cfg ) : ?>
                            <tr>
                                <td><code><?php echo esc_html( $id ); ?></code></td>
                                <td><?php echo esc_html( $cfg['label'] ?? '—' ); ?></td>
                                <td><?php echo esc_html( $cfg['base_price'] ?? 0 ); ?></td>
                                <td><?php echo esc_html( $cfg['currency'] ?? '€' ); ?></td>
                                <td>
                                    <a href="<?php echo esc_url( wp_nonce_url(
                                        add_query_arg( [
                                            'page'       => 'eps-settings',
                                            'eps_delete' => $id,
                                        ], admin_url( 'options-general.php' ) ),
                                        'eps_delete_' . $id
                                    ) ?>" class="eps-btn-delete"
                                       onclick="return confirm('<?php esc_attr_e( 'Supprimer cette configuration ?', 'elementor-price-simulator' ); ?>')">
                                        <?php esc_html_e( 'Supprimer', 'elementor-price-simulator' ); ?>
                                    </a>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    <?php endif; ?>
                </div>

                <!-- Guide rapide -->
                <div class="eps-admin-card eps-admin-guide">
                    <h2><?php esc_html_e( 'Guide d\'utilisation', 'elementor-price-simulator' ); ?></h2>
                    <ol class="eps-guide-steps">
                        <li>
                            <strong><?php esc_html_e( 'Éditez une page avec Elementor', 'elementor-price-simulator' ); ?></strong><br>
                            <?php esc_html_e( 'Ouvrez l\'éditeur Elementor sur la page où vous souhaitez afficher le simulateur.', 'elementor-price-simulator' ); ?>
                        </li>
                        <li>
                            <strong><?php esc_html_e( 'Ajoutez le widget', 'elementor-price-simulator' ); ?></strong><br>
                            <?php esc_html_e( 'Recherchez "Simulateur de Prix" dans le panneau de widgets et glissez-déposez-le sur votre page.', 'elementor-price-simulator' ); ?>
                        </li>
                        <li>
                            <strong><?php esc_html_e( 'Configurez dans Elementor', 'elementor-price-simulator' ); ?></strong><br>
                            <?php esc_html_e( 'Tous les paramètres (tarifs, offres, textes, couleurs) se modifient via les panneaux de contrôle du widget à gauche.', 'elementor-price-simulator' ); ?>
                        </li>
                        <li>
                            <strong><?php esc_html_e( 'Publiez', 'elementor-price-simulator' ); ?></strong><br>
                            <?php esc_html_e( 'Cliquez sur "Publier" — le simulateur est immédiatement interactif pour vos visiteurs.', 'elementor-price-simulator' ); ?>
                        </li>
                    </ol>

                    <h3 style="margin-top:1.5rem;"><?php esc_html_e( 'Logique de tarification', 'elementor-price-simulator' ); ?></h3>
                    <ul class="eps-guide-rules">
                        <li><strong>1 collab :</strong> <?php esc_html_e( 'Forfait fixe défini par offre', 'elementor-price-simulator' ); ?></li>
                        <li><strong>2–4 collabs :</strong> <?php esc_html_e( 'Forfait global fixe', 'elementor-price-simulator' ); ?></li>
                        <li><strong>5–50 collabs :</strong> <?php esc_html_e( 'Prix par collab × effectif (5 tranches configurables)', 'elementor-price-simulator' ); ?></li>
                        <li><strong>51+ collabs :</strong> <?php esc_html_e( '"Sur mesure" — redirige vers le contact', 'elementor-price-simulator' ); ?></li>
                        <li><strong><?php esc_html_e( 'Engagement :', 'elementor-price-simulator' ); ?></strong> <?php esc_html_e( '2 ans = 0%, 3 ans = -5%, 4 ans = -10%, 5 ans = -15%', 'elementor-price-simulator' ); ?></li>
                        <li><strong><?php esc_html_e( 'Avantage fiscal :', 'elementor-price-simulator' ); ?></strong> <?php esc_html_e( '-25% (compte 604, IS)', 'elementor-price-simulator' ); ?></li>
                    </ul>
                </div>

            </div>
        </div>
        <?php
    }
}

// Instancier si on est en admin
if ( is_admin() ) {
    new EPS_Admin();
}
