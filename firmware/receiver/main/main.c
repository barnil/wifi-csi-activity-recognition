#include <stdio.h>
#include <inttypes.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "nvs_flash.h"

static const char *TAG = "CSI_RX";

#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"


/* Called whenever CSI data is received */
static void wifi_csi_rx_cb(void *ctx, wifi_csi_info_t *info)
{
    if (info == NULL || info->buf == NULL) {
        return;
    }

    printf("CSI,len=%d,rssi=%d,rate=%d,channel=%d: ",
           info->len,
           info->rx_ctrl.rssi,
           info->rx_ctrl.rate,
           info->rx_ctrl.channel);

    for (int i = 0; i < info->len; i++) {
        printf("%d", info->buf[i]);

        if (i < info->len - 1) {
            printf(",");
        }
    }

    printf("\n");
}


static void wifi_init(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());

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
        esp_wifi_set_csi_rx_cb(wifi_csi_rx_cb, NULL)
    );

    wifi_csi_config_t csi_config = {
        .lltf_en = true,
        .htltf_en = true,
        .stbc_htltf2_en = true,
        .ltf_merge_en = true,
        .channel_filter_en = false,
        .manu_scale = false,
        .shift = 0,
        .dump_ack_en = false,
    };

    ESP_ERROR_CHECK(
        esp_wifi_set_csi_config(&csi_config)
    );

    ESP_ERROR_CHECK(
        esp_wifi_start()
    );

    ESP_LOGI(TAG, "Connecting to %s", WIFI_SSID);

    ESP_ERROR_CHECK(
        esp_wifi_connect()
    );

    ESP_ERROR_CHECK(
        esp_wifi_set_csi(true)
    );

    ESP_LOGI(TAG, "CSI enabled");
}


void app_main(void)
{
    ESP_LOGI(TAG, "Starting CSI receiver");

    wifi_init();

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
