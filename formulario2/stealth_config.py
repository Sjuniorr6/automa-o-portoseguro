# Configurações Stealth/Anti-Detecção para Selenium
# Este arquivo contém configurações específicas para evitar detecção de automação

# User Agents realistas
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
]

# Configurações de viewport realistas
VIEWPORT_SIZES = [
    "1920,1080",
    "1366,768", 
    "1440,900",
    "1536,864",
    "1280,720",
]

# Configurações de linguagem
LANGUAGES = [
    "pt-BR,pt;q=0.9,en;q=0.8",
    "pt-BR,pt;q=0.9",
    "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
]

# Configurações de timezone
TIMEZONES = [
    "America/Sao_Paulo",
    "America/Bahia",
    "America/Fortaleza",
]

# Configurações de hardware
HARDWARE_CONFIGS = [
    {"concurrency": 8, "memory": 8, "touch_points": 0},
    {"concurrency": 4, "memory": 4, "touch_points": 0},
    {"concurrency": 16, "memory": 16, "touch_points": 0},
]

# Configurações de rede
NETWORK_CONFIGS = [
    {"type": "4g", "rtt": 50, "downlink": 10},
    {"type": "wifi", "rtt": 30, "downlink": 25},
    {"type": "3g", "rtt": 100, "downlink": 5},
]

# Configurações de plugins
PLUGIN_CONFIGS = [
    [1, 2, 3, 4, 5],
    [1, 2, 3],
    [1, 2, 3, 4, 5, 6, 7],
]

# Configurações de comportamento humano
HUMAN_BEHAVIOR = {
    "typing_speed": {
        "min_delay": 0.05,
        "max_delay": 0.15,
    },
    "click_delay": {
        "min_delay": 0.1,
        "max_delay": 0.3,
    },
    "page_delay": {
        "min_delay": 2.0,
        "max_delay": 5.0,
    },
    "scroll_delay": {
        "min_delay": 0.5,
        "max_delay": 1.5,
    },
    "mouse_movement": {
        "enabled": True,
        "random_moves": True,
    },
}

# Configurações de stealth específicas
STEALTH_CONFIG = {
    "disable_webdriver": True,
    "disable_automation": True,
    "mask_plugins": True,
    "mask_languages": True,
    "mask_hardware": True,
    "mask_network": True,
    "mask_permissions": True,
    "mask_geolocation": True,
    "mask_media_devices": True,
    "mask_service_worker": True,
    "mask_storage": True,
    "mask_credentials": True,
    "mask_modern_apis": True,
    "simulate_human_behavior": True,
    "random_delays": True,
    "mouse_movements": True,
    "scroll_behavior": True,
}

# Configurações de detecção de bot
BOT_DETECTION_EVASION = {
    "remove_webdriver_property": True,
    "remove_automation_flags": True,
    "simulate_real_browser": True,
    "mask_selenium_signatures": True,
    "simulate_user_interaction": True,
    "randomize_timing": True,
    "simulate_mouse_movements": True,
    "simulate_keyboard_events": True,
    "simulate_scroll_events": True,
    "simulate_focus_events": True,
    "simulate_blur_events": True,
    "simulate_change_events": True,
    "simulate_input_events": True,
    "simulate_submit_events": True,
    "simulate_resize_events": True,
    "simulate_orientation_events": True,
    "simulate_visibility_events": True,
    "simulate_online_events": True,
    "simulate_offline_events": True,
    "simulate_storage_events": True,
}

# Configurações de fingerprinting
FINGERPRINTING_PROTECTION = {
    "canvas_fingerprint": True,
    "webgl_fingerprint": True,
    "audio_fingerprint": True,
    "font_fingerprint": True,
    "screen_fingerprint": True,
    "timezone_fingerprint": True,
    "language_fingerprint": True,
    "platform_fingerprint": True,
    "vendor_fingerprint": True,
    "user_agent_fingerprint": True,
    "connection_fingerprint": True,
    "hardware_fingerprint": True,
    "battery_fingerprint": True,
    "memory_fingerprint": True,
    "device_fingerprint": True,
    "touch_fingerprint": True,
    "pointer_fingerprint": True,
    "media_fingerprint": True,
    "codec_fingerprint": True,
    "plugin_fingerprint": True,
    "mime_fingerprint": True,
    "do_not_track_fingerprint": True,
    "cookie_fingerprint": True,
    "session_storage_fingerprint": True,
    "local_storage_fingerprint": True,
    "indexed_db_fingerprint": True,
    "websql_fingerprint": True,
    "file_system_fingerprint": True,
    "quota_fingerprint": True,
    "permission_fingerprint": True,
    "notification_fingerprint": True,
    "push_fingerprint": True,
    "service_worker_fingerprint": True,
    "background_sync_fingerprint": True,
    "periodic_sync_fingerprint": True,
    "background_fetch_fingerprint": True,
    "content_index_fingerprint": True,
    "navigator_fingerprint": True,
    "window_fingerprint": True,
    "document_fingerprint": True,
    "location_fingerprint": True,
    "history_fingerprint": True,
    "screen_fingerprint": True,
    "visual_viewport_fingerprint": True,
    "performance_fingerprint": True,
    "timing_fingerprint": True,
    "navigation_fingerprint": True,
    "memory_fingerprint": True,
    "device_memory_fingerprint": True,
    "hardware_concurrency_fingerprint": True,
    "connection_fingerprint": True,
    "network_information_fingerprint": True,
    "battery_fingerprint": True,
    "vibration_fingerprint": True,
    "ambient_light_fingerprint": True,
    "proximity_fingerprint": True,
    "orientation_fingerprint": True,
    "motion_fingerprint": True,
    "device_orientation_fingerprint": True,
    "device_motion_fingerprint": True,
    "geolocation_fingerprint": True,
    "media_devices_fingerprint": True,
    "media_capabilities_fingerprint": True,
    "media_session_fingerprint": True,
    "presentation_fingerprint": True,
    "remote_playback_fingerprint": True,
    "wake_lock_fingerprint": True,
    "idle_detection_fingerprint": True,
    "scheduling_fingerprint": True,
    "scheduler_fingerprint": True,
    "priority_hints_fingerprint": True,
    "resource_hints_fingerprint": True,
    "preload_fingerprint": True,
    "prefetch_fingerprint": True,
    "prerender_fingerprint": True,
    "dns_prefetch_fingerprint": True,
    "connect_fingerprint": True,
    "module_preload_fingerprint": True,
    "module_prefetch_fingerprint": True,
    "module_prerender_fingerprint": True,
    "module_dns_prefetch_fingerprint": True,
    "module_connect_fingerprint": True,
    "module_preload_fingerprint": True,
    "module_prefetch_fingerprint": True,
    "module_prerender_fingerprint": True,
    "module_dns_prefetch_fingerprint": True,
    "module_connect_fingerprint": True,
} 