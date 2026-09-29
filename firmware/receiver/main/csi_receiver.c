#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "nvs_flash.h"

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"

#define WIFI_SSID     "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

static const char *TAG = "CSI_RECEIVER";

/*
 * CSI callback.
 *
 * This function is called by the ESP32 Wi-Fi driver whenever
 * CSI information is available.
 */
static void csi_rx_callback(void *ctx, wifi_csi_info_t *data)
{
    if (data == NULL || data->buf == NULL || data->len == 0) {
        return;
    }

    printf("CSI,%u,%u",
           (unsigned int)data->rx_seq,
           (unsigned int)data->len);

    for (int i = 0; i < data->len; i++) {
        printf(",%d", data->buf[i]);
    }

    printf("\n");
}

static void wifi_init_sta(void)
{
    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());

    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();

    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASSWORD,
        },
    };

    ESP_ERROR_CHECK(
        esp_wifi_set_mode(WIFI_MODE_STA)
    );

    ESP_ERROR_CHECK(
        esp_wifi_set_config(WIFI_IF_STA, &wifi_config)
    );

    ESP_ERROR_CHECK(
        esp_wifi_start()
    );

    ESP_LOGI(TAG, "Connecting to Wi-Fi: %s", WIFI_SSID);

    ESP_ERROR_CHECK(
        esp_wifi_connect()
    );
}

static void csi_init(void)
{
    /*
     * Configuration for the classic ESP32 CSI implementation.
     *
     * These fields correspond to the wifi_csi_config_t structure
     * we inspected in your ESP-IDF 6.0.2 installation.
     */
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));

    wifi_csi_config_t csi_config = {
        .lltf_en = true,
        .htltf_en = true,
        .stbc_htltf2_en = true,
        .ltf_merge_en = true,
        .channel_filter_en = true,
        .manu_scale = false,
        .shift = 0,
        .dump_ack_en = false,
    };

    ESP_ERROR_CHECK(
        esp_wifi_set_csi_config(&csi_config)
    );

    ESP_ERROR_CHECK(
        esp_wifi_set_csi_rx_cb(csi_rx_callback, NULL)
    );

    ESP_ERROR_CHECK(
        esp_wifi_set_csi(true)
    );

    ESP_LOGI(TAG, "CSI enabled");
}

void app_main(void)
{
    /*
     * Initialize NVS.
     * Wi-Fi uses NVS for persistent configuration/calibration data.
     */
    esp_err_t ret = nvs_flash_init();

    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {

        ESP_ERROR_CHECK(nvs_flash_erase());

        ret = nvs_flash_init();
    }

    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Starting CSI receiver");

    wifi_init_sta();

    /*
     * Give Wi-Fi a moment to initialize.
     */
    vTaskDelay(pdMS_TO_TICKS(2000));

    csi_init();

    ESP_LOGI(TAG, "CSI receiver running");

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
