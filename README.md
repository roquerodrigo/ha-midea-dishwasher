# Midea Dishwasher

<!-- ha-marketplace:exclude-start -->
[![CI](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/ci.yml/badge.svg)](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/roquerodrigo/ha-midea-dishwasher)](https://github.com/roquerodrigo/ha-midea-dishwasher/releases/latest)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/roquerodrigo)

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=roquerodrigo&repository=ha-midea-dishwasher&category=integration)
<!-- ha-marketplace:exclude-end -->

Follow your Midea dishwasher from Home Assistant: what it is doing, how long
the cycle still takes, whether the door is open and when the rinse aid or the
salt runs out. You can also start a program, cancel it and turn the dishwasher
on or off. Home Assistant talks to the dishwasher on your local network, so
day to day nothing goes through Midea's cloud. The protocol is implemented in
the [midea-dishwasher-api](https://github.com/roquerodrigo/midea-dishwasher-api)
library.

## Features

- See the status, the program and the wash stage of the current cycle, with
  the time remaining and how much of the cycle is done.
- Get a warning when the rinse aid or the dishwasher salt runs out.
- Know when the door is open, and read the water temperature in the tub.
- Start an ECO or Intensive cycle with one button, or any of the 14 programs
  from an automation, with or without extra drying.
- Cancel a running cycle, turn the dishwasher on or off and set the rinse aid
  level.
- Get a repair notice in Home Assistant when the dishwasher stops answering.

## Requirements

- Home Assistant 2026.8.0 or newer.
- A Midea dishwasher with Wi-Fi, added to your Midea app account and connected
  to a network that Home Assistant can reach.
- The dishwasher's IP address, device ID, token and key. See Getting the token
  and key below.

<!-- ha-marketplace:exclude-start -->
## Installation

### Home Assistant Marketplace (recommended)

1. Select the **Open your Home Assistant instance** button above, or go to
   **Settings → Marketplace**, select **Add from link** in the upper right
   corner, enter `roquerodrigo/ha-midea-dishwasher` and select **Add**.
2. Select **Install**.
3. Restart Home Assistant.

The Marketplace comes with Home Assistant 2026.11 and later. On older
versions, add this repository to HACS as a custom repository of type
**Integration** and install it from there.

### Manual

1. Download `midea_dishwasher.zip` from the
   [latest release](https://github.com/roquerodrigo/ha-midea-dishwasher/releases/latest).
2. Extract it into `config/custom_components/midea_dishwasher/`.
3. Restart Home Assistant.
<!-- ha-marketplace:exclude-end -->

## Configuration

Go to **Settings → Devices & services → Add integration**, search for
**Midea Dishwasher** and fill in the form.

| Field       | What to enter                                              | Default |
|-------------|------------------------------------------------------------|---------|
| IP address  | The address of the dishwasher on your network              |         |
| Port        | The dishwasher's local port, from 1 to 65535               | 6444    |
| Device ID   | The dishwasher's numeric ID                                |         |
| Token (hex) | The token, 128 hexadecimal characters                      |         |
| Key (hex)   | The key, 64 hexadecimal characters                         |         |

Home Assistant connects to the dishwasher before saving, so a wrong address or
wrong credentials are reported right away. Give the dishwasher a fixed IP
address in your router, otherwise it can stop answering after a router
restart.

To change any of these later, open the integration and select
**Reconfigure**. If the dishwasher stops accepting the token and key, Home
Assistant asks you for new ones. In both cases the device ID must stay the
same: you cannot point an existing entry at another dishwasher.

### Getting the token and key

The token and key are issued by Midea's cloud for your dishwasher, and
Home Assistant cannot fetch them for you. Community tools that sign in with
your Midea app account can read them, for example
[msmart-ng](https://github.com/mill1000/midea-msmart) and
[midea-beautiful-air](https://github.com/nbogojevic/midea-beautiful-air).
These tools were written for Midea air conditioners, so check that the one you
choose lists your dishwasher, and follow its instructions. With
midea-beautiful-air, for example:

```bash
midea-beautiful-air-cli discover --account YOUR_EMAIL --password YOUR_PASSWORD --credentials
```

Copy the device ID shown next to the token and key as well.

## Options

Open the integration and select **Configure**.

| Setting                    | Default | Range           | Effect                                     |
|----------------------------|---------|-----------------|--------------------------------------------|
| Polling interval (seconds) | 30      | 10 or more      | How often Home Assistant reads the dishwasher |

The integration reloads when you save the options.

## Entities

All entities belong to one device, **Dishwasher**.

### Sensors

| Entity         | Type          | Shows                                                                 |
|----------------|---------------|-----------------------------------------------------------------------|
| Status         | Sensor        | Power off, Idle, Scheduled, Running, Error or Soft gear               |
| Program        | Sensor        | The running program (see the list under Actions)                      |
| Progress       | Sensor        | Idle, Pre-wash, Main wash, Rinse, Dry or Finish                       |
| Time remaining | Sensor        | Time left in the cycle                                                |
| Cycle progress | Sensor        | Percentage of the cycle already done, empty when no cycle is running |
| Temperature    | Sensor        | Water temperature in the tub, in °C                                   |
| Error code     | Sensor        | None, Water supply, Heating, Overflow or Water valve. Diagnostic      |
| Door           | Binary sensor | Open or Closed                                                        |
| Extra drying   | Binary sensor | On when the current cycle includes extra drying                       |
| Rinse aid      | Binary sensor | Problem when the rinse aid has run out. Diagnostic                    |
| Salt           | Binary sensor | Problem when the dishwasher salt has run out. Diagnostic              |

### Controls

| Entity                | Type   | Does                                                    |
|-----------------------|--------|---------------------------------------------------------|
| Power                 | Switch | Turns the dishwasher on or off                          |
| Rinse-aid level       | Number | Sets the rinse aid dose, from 1 to 5                    |
| Start ECO cycle       | Button | Starts the ECO program without extra drying             |
| Start intensive cycle | Button | Starts the Intensive program with extra drying          |
| Cancel cycle          | Button | Cancels the running cycle                               |

The dishwasher only reports the minutes left. Cycle progress takes the longest
time remaining seen since the cycle started as the length of the cycle, and
keeps it across Home Assistant restarts. The entity also shows that length in
its `cycle_total_minutes` attribute.

## Actions

### Start cycle (`midea_dishwasher.start_cycle`)

Starts any program, with or without extra drying.

| Field             | Required | What it does                                       |
|-------------------|----------|----------------------------------------------------|
| `config_entry_id` | Yes      | The dishwasher to control. Pick it from the list in the action editor |
| `mode`            | Yes      | The program to run, from the list below             |
| `extra_drying`    | No       | Add extra drying at the end of the cycle. Default `false` |

| `mode`      | Program     |
|-------------|-------------|
| `auto`      | Auto        |
| `intensive` | Intensive   |
| `normal`    | Normal      |
| `eco`       | ECO         |
| `glass`     | Glassware   |
| `90min`     | 90 minutes  |
| `1hour`     | 1 hour      |
| `rapid`     | Rapid       |
| `soak`      | Pre-rinse   |
| `3in1`      | 3-in-1      |
| `hygiene`   | Hygiene     |
| `quiet`     | Quiet       |
| `party`     | Party       |
| `fruit`     | Fruits      |

```yaml
action: midea_dishwasher.start_cycle
data:
  config_entry_id: YOUR_CONFIG_ENTRY_ID
  mode: eco
  extra_drying: true
```

If the dishwasher does not accept the command, the action fails with an error
that you can see in the automation trace.

## How it works

Home Assistant reads the dishwasher over your local network every polling
interval, 30 seconds by default. The token and key come from Midea's cloud
once, during setup. After that, everything stays on your local network.

After a button, the switch, the rinse aid level or the action sends a command,
Home Assistant reads the dishwasher again so the entities catch up. The
dishwasher can take a few seconds to show the change.

If three updates in a row fail to reach the dishwasher, a **Dishwasher is
unreachable** notice appears under **Settings → System → Repairs**. It goes
away on its own as soon as the dishwasher answers again.

## Troubleshooting

**Setup says the token must be 128 hex chars and the key 64.** The token or
the key is incomplete or contains characters other than 0 to 9 and a to f.
Copy them again from the tool you used.

**Setup says the dishwasher rejected the token/key.** The token and key do not
belong to this dishwasher, or they are no longer valid. Read them again from
your Midea account. Check that the device ID matches the dishwasher at that IP
address.

**Setup says it is unable to reach the dishwasher.** Check that the dishwasher
is on, connected to Wi-Fi, and that the IP address and port are right.

**A Dishwasher is unreachable notice appears.** The dishwasher is off, out of
the network, or its IP address changed. Fix the address with **Reconfigure**
and give it a fixed IP address in your router.

**Reconfigure says the credentials belong to a different dishwasher.** The
device ID you entered is not the one of this entry. Add the other dishwasher as
a new entry instead.

**Something else is wrong.** Enable debug logging from the integration's menu,
reproduce the problem, then download the diagnostics and attach both to an
[issue](https://github.com/roquerodrigo/ha-midea-dishwasher/issues). The
token, the key and the device ID are removed from the diagnostics file.

## Known limitations

- Home Assistant cannot get the token and key from Midea's cloud. You read
  them once with another tool.
- The dishwasher serves one connection at a time. A command can fail if the
  dishwasher is busy answering another request. Try it again.
- Cycle progress is an estimate. If Home Assistant first sees a cycle when it
  is already under way, the percentage counts from that moment.

## Support

This integration is built and maintained on personal time, on hardware bought
for the purpose. If it is useful to you, consider
[sponsoring the work](https://github.com/sponsors/roquerodrigo). It keeps the
devices, the testing and the releases coming.

<!-- ha-marketplace:exclude-start -->
## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup and
workflow, and [CODE_STYLE.md](CODE_STYLE.md) for the code conventions.

## License

[MIT](LICENSE)
<!-- ha-marketplace:exclude-end -->
