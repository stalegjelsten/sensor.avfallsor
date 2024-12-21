# sensor.avfallsor
This is my fork of [Hellowlol's](https://github.com/custom-components/sensor.avfallsor/commits?author=Hellowlol) [Avfall Sør sensor](https://github.com/custom-components/sensor.avfallsor).

Simple sensor for avfallsor (garbage pickup)



## Installation
Install using hacs.

Add this repo as a custom repository in HACS and search for `avfallsor`. Pick this one.

## Configuration options
Key | Type | Required | Default | Description
-- | -- | -- | -- | --
`address` | `string` | `False` | `""` | Address for garbage pickup
`street_id` | `string` | `False` | `""` | Go to https://avfallsor.no/henting-av-avfall/finn-hentedag/ enter the address and the hour number, select your adresse in the dropdown. After that you will be redirected to a url that look like: ```https://avfallsor.no/henting-av-avfall/finn-hentedag/c7b62b91-1f99-41a7-927d-5c3dc91805ca/``` grab the hash at the end.

The sensor tries to find the your address (to find the pickup dates for your address) in this order:
1. `street_id`
2. `address`
3. Lat and lon that you entered when you setup home assistant.

### Integrations
- In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "avfallsor"

See the `lovelace_example` folder for config example


[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/sensor.avfallsor.svg?style=for-the-badge
[commits]: https://github.com/custom-components/sensor.avfallsor/commits/master
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/custom-components/blueprint.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/custom-components/blueprint.svg?style=for-the-badge
[releases]: https://github.com/custom-components/sensor.avfallsor/releases
