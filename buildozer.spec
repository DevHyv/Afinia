[app]
title = Afinia
package.name = afinia
package.domain = org.afinia

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# Solo dependencias básicas (Kivy ya incluye lo necesario para la interfaz)
requirements = python3,kivy

# Permisos para acceder al micrófono de Android
android.permissions = RECORD_AUDIO, INTERNET

orientation = portrait
fullscreen = 0

# Arquitectura ARM64 (cubre la mayoría de dispositivos actuales)
android.archs = arm64-v8a

# API mínima y objetivo
android.minapi = 21
android.api = 33

# NDK estable recomendado
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
