<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Calcul du prix en fonction des données du formulaire et de la config
 */
class EPS_Calculator {

    private $config;

    public function __construct( array $config ) {
        $this->config = $config;
    }

    /**
     * Calcule le prix total à partir des données du formulaire.
     *
     * @param array $form_data  Tableau associatif { field_id => value }
     * @return array { price, formatted, breakdown }
     */
    public function calculate( array $form_data ) {
        $base_price = isset( $this->config['base_price'] ) ? (float) $this->config['base_price'] : 0;
        $currency   = isset( $this->config['currency'] )   ? $this->config['currency']            : '€';
        $fields     = isset( $this->config['fields'] )     ? (array) $this->config['fields']      : [];

        $total     = $base_price;
        $percent_bonus = 0;
        $breakdown = [];

        if ( $base_price > 0 ) {
            $breakdown[] = [
                'label' => __( 'Prix de base', 'elementor-price-simulator' ),
                'price' => $base_price,
            ];
        }

        foreach ( $fields as $field ) {
            $field_id = isset( $field['id'] ) ? $field['id'] : '';
            if ( empty( $field_id ) || ! isset( $form_data[ $field_id ] ) ) {
                continue;
            }

            $value = $form_data[ $field_id ];
            $type  = isset( $field['type'] ) ? $field['type'] : 'text';

            switch ( $type ) {
                case 'number':
                case 'range':
                    $result = $this->calc_number( $field, $value );
                    if ( $result['price'] != 0 ) {
                        $total       += $result['price'];
                        $breakdown[]  = $result;
                    }
                    break;

                case 'select':
                case 'radio':
                    $result = $this->calc_option( $field, $value );
                    if ( $result['price'] != 0 ) {
                        $total       += $result['price'];
                        $breakdown[]  = $result;
                    }
                    break;

                case 'checkbox_group':
                    $values  = is_array( $value ) ? $value : [ $value ];
                    $results = $this->calc_checkbox_group( $field, $values );
                    foreach ( $results as $r ) {
                        if ( $r['price'] != 0 ) {
                            $total       += $r['price'];
                            $breakdown[]  = $r;
                        }
                    }
                    break;

                case 'toggle':
                case 'checkbox':
                    if ( $value && $value !== 'false' && $value !== '0' ) {
                        $result = $this->calc_toggle( $field, $total );
                        if ( isset( $result['percent'] ) ) {
                            $percent_bonus += $result['percent'];
                            $breakdown[]    = $result;
                        } elseif ( $result['price'] != 0 ) {
                            $total       += $result['price'];
                            $breakdown[]  = $result;
                        }
                    }
                    break;
            }
        }

        // Appliquer les pourcentages en dernier
        if ( $percent_bonus != 0 ) {
            $bonus_amount = round( $total * $percent_bonus / 100, 2 );
            $total       += $bonus_amount;
        }

        $total = round( $total, 2 );

        return [
            'price'     => $total,
            'formatted' => number_format( $total, 2, ',', ' ' ) . ' ' . $currency,
            'currency'  => $currency,
            'breakdown' => $breakdown,
        ];
    }

    private function calc_number( $field, $value ) {
        $value = (float) $value;
        $rule  = isset( $field['price_rule'] ) ? $field['price_rule'] : [];
        $price = 0;

        if ( empty( $rule ) ) {
            $price = $value;
        } else {
            switch ( $rule['type'] ) {
                case 'multiply':
                    $price = $value * (float) $rule['value'];
                    break;
                case 'fixed':
                    $price = (float) $rule['value'];
                    break;
                case 'per_unit':
                    $step  = isset( $rule['step'] )  ? (float) $rule['step']  : 1;
                    $price = ( $value / $step ) * (float) $rule['value'];
                    break;
                default:
                    $price = $value;
            }
        }

        return [
            'label' => isset( $field['label'] ) ? $field['label'] . ' (' . $value . ')' : $value,
            'price' => round( $price, 2 ),
        ];
    }

    private function calc_option( $field, $value ) {
        $options = isset( $field['options'] ) ? (array) $field['options'] : [];
        foreach ( $options as $option ) {
            if ( isset( $option['value'] ) && $option['value'] === $value ) {
                return [
                    'label' => isset( $option['label'] ) ? $option['label'] : $value,
                    'price' => isset( $option['price'] ) ? (float) $option['price'] : 0,
                ];
            }
        }
        return [ 'label' => $value, 'price' => 0 ];
    }

    private function calc_checkbox_group( $field, $values ) {
        $options = isset( $field['options'] ) ? (array) $field['options'] : [];
        $results = [];
        foreach ( $options as $option ) {
            if ( isset( $option['value'] ) && in_array( $option['value'], $values ) ) {
                $results[] = [
                    'label' => isset( $option['label'] ) ? $option['label'] : $option['value'],
                    'price' => isset( $option['price'] ) ? (float) $option['price'] : 0,
                ];
            }
        }
        return $results;
    }

    private function calc_toggle( $field, $current_total ) {
        $rule = isset( $field['price_rule'] ) ? $field['price_rule'] : [];

        if ( ! empty( $rule ) && $rule['type'] === 'percent' ) {
            $pct = (float) $rule['value'];
            return [
                'label'   => isset( $field['label'] ) ? $field['label'] : '',
                'price'   => round( $current_total * $pct / 100, 2 ),
                'percent' => $pct,
            ];
        }

        $price = isset( $field['price'] ) ? (float) $field['price'] : 0;
        return [
            'label' => isset( $field['label'] ) ? $field['label'] : '',
            'price' => $price,
        ];
    }
}
