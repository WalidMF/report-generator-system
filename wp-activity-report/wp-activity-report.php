<?php
/**
 * Plugin Name: Activity Report Form (Flask)
 * Description: Adds a shortcode [activity_report_form] that renders the activity form and posts it to an external Flask API to generate a PDF and download it.
 * Version: 0.1
 * Author: (auto-generated)
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

function war_enqueue_assets() {
    wp_register_style('war-styles', plugins_url('assets/styles.css', __FILE__));
    wp_register_script('war-script', plugins_url('assets/script.js', __FILE__), array('jquery'), false, true);
    wp_localize_script('war-script', 'warSettings', array(
        // Change this to the Flask API base URL if needed (no trailing slash)
        'apiBase' => esc_url_raw('http://127.0.0.1:5000/api')
    ));
    wp_enqueue_style('war-styles');
    wp_enqueue_script('war-script');
}
add_action('wp_enqueue_scripts', 'war_enqueue_assets');

function war_render_form() {
    ob_start();
    ?>
    <div class="war-container">
        <form id="warForm" class="war-form" enctype="multipart/form-data">
            <div class="war-row">
                <label for="activityName">اسم النشاط</label>
                <input id="activityName" name="activityName" required />
            </div>
            <div class="war-row">
                <label for="executionDate">تاريخ التنفيذ</label>
                <input id="executionDate" name="executionDate" required />
            </div>
            <div class="war-row">
                <label for="executorName">مسؤول التنفيذ</label>
                <input id="executorName" name="executorName" required />
            </div>
            <div class="war-row">
                <label for="location">مكان التنفيذ</label>
                <input id="location" name="location" required />
            </div>
            <div class="war-row">
                <label for="targetGroup">الفئة المستهدفة</label>
                <input id="targetGroup" name="targetGroup" required />
            </div>
            <div class="war-row">
                <label for="images">صور الشواهد (٤ صور)</label>
                <input id="images" name="images" type="file" accept="image/*" multiple required />
            </div>
            <div class="war-row war-actions">
                <button id="warSubmit" type="submit">إنشاء التقرير</button>
                <span id="warStatus" class="war-status"></span>
            </div>
        </form>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('activity_report_form', 'war_render_form');

?>
