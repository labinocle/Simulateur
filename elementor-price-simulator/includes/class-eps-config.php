<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Gestion de la configuration des simulateurs
 */
class EPS_Config {

    /**
     * Récupère la configuration d'un simulateur par son ID.
     * Si $id est vide, retourne la première configuration disponible.
     */
    public static function get( $id = '' ) {
        $all = self::get_all();

        if ( empty( $all ) ) {
            return [];
        }

        if ( ! empty( $id ) && isset( $all[ $id ] ) ) {
            return $all[ $id ];
        }

        // Retourne la première config par défaut
        return reset( $all );
    }

    /**
     * Retourne toutes les configurations enregistrées.
     */
    public static function get_all() {
        return (array) get_option( EPS_OPTION_KEY, [] );
    }

    /**
     * Sauvegarde une configuration.
     */
    public static function save( $id, $config ) {
        $all         = self::get_all();
        $all[ $id ]  = $config;
        return update_option( EPS_OPTION_KEY, $all );
    }

    /**
     * Supprime une configuration.
     */
    public static function delete( $id ) {
        $all = self::get_all();
        unset( $all[ $id ] );
        return update_option( EPS_OPTION_KEY, $all );
    }

    /**
     * Retourne la liste des configs sous forme de choix pour Elementor.
     */
    public static function get_elementor_choices() {
        $choices = [];
        foreach ( self::get_all() as $id => $config ) {
            $choices[ $id ] = isset( $config['label'] ) ? $config['label'] : $id;
        }
        return $choices;
    }

    /**
     * Génère un ID unique à partir du label.
     */
    public static function generate_id( $label ) {
        return sanitize_key( str_replace( ' ', '_', strtolower( $label ) ) . '_' . time() );
    }
}
