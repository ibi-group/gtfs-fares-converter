# GTFS Fares Converter

Converts a GTFS feed's Fares V1 info to Fares V2 info.


## Usage

If not using the pip package:

```bash
pip install -r ./requirements.txt
python __init__.py /path/to/current-fares-v1-gtfs.zip /path/to/new-fares-v2-gtfs.zip
```

## Notes

- The script creates a temporary directory under `/tmp/gtfs/`. Make sure you have write permissions.
- Paid transfers are not currently supported.
- The `contains_id` field in fare_rules.txt is not currently supported.
