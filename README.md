# TeslaFi Home Asisstant Integration

Custom integration for Tesla Vehicles using [TeslaFi](https://teslafi.com/) API feed.

**Prior To Installation**

You will need your TeslaFi API Token. You can obtain the API token [here](https://teslafi.com/api.php)
(note you will need to be logged in first).

Also pay attention to the checkboxes on the "Commands" tab. Any command that is not enabled here
will fail when trying to use it.

Note that TeslaFi allows monitoring only one vehicle per account. If you have multiple Tesla
vehicles, you would need to create multiple TeslaFi accounts; and therefore you would have multiple
API Tokens.

## Installation

### With HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

1. Open HACS Settings and add this repository (https://github.com/jhansche/ha-teslafi/)
   as a Custom Repository (use **Integration** as the category).
2. The `TeslaFi` page should automatically load (or find it in the HACS Store)
3. Click `Install`
4. Continue to [Setup](README.md#Setup)

Alternatively, click on the button below to add the repository:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&repository=ha-teslafi&owner=jhansche)

### Manul

Copy the `teslafi` directory from `custom_components` in this repository,
and place inside your Home Assistant Core installation's `custom_components` directory.

## Setup

1. Install this integration.
2. Navigate to the Home Assistant Integrations page (Settings --> Devices & Services)
3. Click the `+ Add Integration` button in the bottom-right
4. Search for `TeslaFi`
5. Enter your API Token from above

Alternatively, click on the button below to add the integration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=teslafi)
