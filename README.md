# 🍴 Octopus Spain (FORK de Marco) — con Consumo y Vertido

> ⚠️ **Este es un fork personal de [`miguelangellv/ha-octopus-spain`](https://github.com/miguelangellv/ha-octopus-spain)**, NO el componente oficial.
> Si en HACS dudas cuál es: **este es `marcoaperez/ha-octopus-spain`**.
>
> **Qué añade respecto al original:**
> - 📊 **Consumo eléctrico horario** del contador inteligente como *estadísticas de largo plazo* → se integra en el **panel de Energía** de Home Assistant.
> - 🔌 **Vertido/excedente** (si hay autoconsumo) como estadística independiente.
> - 🗓️ Sensor **`Consumo Último Día`** (kWh del último día disponible).
> - Backfill inicial de **12 meses** + actualización diaria incremental.
>
> Mantiene todo lo del original (Solar Wallet, crédito, última factura, precios por periodo). Integración de **solo lectura**.
> Detalle técnico en los commits de la rama `feature/consumo-vertido`.

---

## ¿Qué es Octopus Energy?

[Octopus Energy](https://octopusenergy.es/) es una comercializadora eléctrica española.

Entre otras ventajas, dispone de la **Solar Wallet**, un servicio que permite acumular crédito obtenido
por los excedentes solares para reducir a 0€ la factura así como acumular para posteriores facturas.

## ¿Qué hace el componente Octopus Spain?

Este componente conecta con tu cuenta de _Octopus Energy_ para obtener el estado actual de tu **Solar Wallet**
así como los datos básicos de última factura.

Este componente ha sido revisado por los ingenerios de _Octopus Energy_ y ha recibido su visto bueno.

## Instalación

Puedes instalar el componente usando HACS:

### Directa usando _My Home Assistant_

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=miguelangellv&repository=ha-octopus-spain&category=integration)

### Manual

```
HACS -> Integraciones -> Tres puntitos -> Repositorios Personalizados
```

Copias la URL del reposotiro ( https://github.com/MiguelAngelLV/octopus_spain ), como categoría seleccionas _Integración_ y pulsas en _Añadir_.

## Configuración

Una vez instalado, ve a _Dispositivos y Servicios -> Añadir Integración_ y busca _Octopus_.

El asistente te solicitará tu email y contraseña de [Octopus Energy](https://octopusenergy.es/)

## Entidades

Una vez configurado el componente, tendrás dos entidades por cada cuenta que tengas asociada a tu email (normalmente una).

### Solar Wallet

La entidad Solar Wallet devuelve el valor actual de tu Solar Wallet. Este valor (en euros) estará actualizado al de tu última factura. Actualmente no se puede consultar en tiempo real.

## Octopus Credit

La entidad Octopus Credit devuelve el valor actual de tu crédito en Octopus obtenido por cuentas referedidas u otras posibles bonificaciones.

### Última Factura

Esta entidad devuelve el coste de tu última factura.

Adicionalmente, en los atributos, están disponibles las fechas de emisión de esa factura así el periodo (inicio y final) de la misma.

## Uso

Podrás usar estas etidades para visualizar el estado así como crear automatizaciones para informate, por ejemplo,
cuando se produzca un cambio en el atributo "Emitida" de última fáctura.

Una forma de representar los datos sería esta:

```yaml
title: Octopus Spain
type: entities
entities:
  - entity: sensor.ultima_factura_octopus
  - entity: sensor.solar_wallet
  - entity: sensor.octopus_credit
  - type: attribute
    entity: sensor.ultima_factura_octopus
    name: Inicio
    icon: mdi:calendar-start
    attribute: Inicio
  - type: attribute
    entity: sensor.ultima_factura_octopus
    name: Fin
    icon: mdi:calendar-end
    attribute: Fin
  - type: attribute
    entity: sensor.ultima_factura_octopus
    name: Emitida
    icon: mdi:email-fast-outline
    attribute: Emitida
```

![card.png](img/card.png)

## Videotutorial

[![Octopus Spain](http://img.youtube.com/vi/fJ1W_wACbfw/0.jpg)](http://www.youtube.com/watch?v=fJ1W_wACbfw)
