# espr

Eskom Se Push Reminder

> A simple polybar module to remind you when loadshedding is scheduled.
> (Should also work with any other status bar that supports custom scripts)

## Installation

1) Clone this repo to your polybar scripts directory
```bash
cd /path/to/your/polybar/scripts
git clone https://github.com/Rec1dite/espr
```

2) Register for an API token at [ESP's Gumroad page](https://eskomsepush.gumroad.com/l/api)

3) Add your API token to the `token` file in the cloned repo so it looks as follows:
```bash
XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX
```

4) Use the `search.py` helper script to find the area you want to monitor
```bash
python3 search.py
```

5) Copy the correct area object from the json and add it to the CONFIG variable in `espr.py`
```python
CONFIG = {
    "id": "region-x-area",  # IMPORTANT: This is the area you want to monitor
    "name": "YOURAREA (x)", # You can change this to whatever you want
    "region": "YourRegion", # You can change this to whatever you want
    "refresh": 30,          # How often to refresh the cached data in minutes
}
```


6) Add the espr module to your polybar config and set the interval to your liking

```ini
[module/espr]
type = custom/script
exec = /path/to/your/polybar/scripts/espr/espr.py "<when>"
interval = 60
```

7) Customize the `"<when>"` argument to your liking.
Currently supported tags are:
- `<areaName>`: Show the area name as specified in your CONFIG
- `<areaRegion>`: Show the area region as specified in your CONFIG
- `<when>`: If currently loadshedding show when it ends; else show the next expected stage
- `<next>`: Show when the next expected stage will start

Some examples:
```ini
exec = /path/to/your/polybar/scripts/espr/espr.py "<areaName> ⚡ <next>"
exec = /path/to/your/polybar/scripts/espr/espr.py "<when> (<areaRegion>)"
```

## Screenshots