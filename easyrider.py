import json
import re
import pandas as pd

class EasyRider:
    def __init__(self, buses_and_stops):
        self.buses_and_stops = buses_and_stops

    def run(self):
        validation_results = self.field_validation()
        self.print_validation_errors(validation_results)
        self.bus_line_info()

    def bus_line_info(self):
        buses_df = pd.DataFrame(json.loads(self.buses_and_stops))

        # Count number of stops per bus
        stop_counts = buses_df.groupby("bus_id").agg(total_stops=("stop_id", "count"))

        # Check if route contains both Start and Finish type stops
        start_finish_counts = buses_df.groupby("bus_id")["stop_type"].agg(
            has_start=lambda s: (s == "S").any(),
            has_finish=lambda s: (s == "F").any()
        )
        start_finish_counts["has_start_and_finish"] = (
                start_finish_counts["has_start"] & start_finish_counts["has_finish"]
        )

        # Combine summary stats into one DataFrame
        summary_df = pd.concat([stop_counts, start_finish_counts], axis=1)

        print('\nLine names and number of stops:')
        for bus_id, row in summary_df.iterrows():
            print(f"bus_id: {bus_id} stops: {row['total_stops']}")
            if not row["has_start_and_finish"]:
                print(f"There is no start or end stop for the line: {bus_id}")

        if not (~start_finish_counts["has_start_and_finish"]).any():
            start_stops = buses_df[buses_df["stop_type"] == "S"]["stop_name"].unique().tolist()
            finish_stops = buses_df[buses_df["stop_type"] == "F"]["stop_name"].unique().tolist()
            transfer_stops = (
                buses_df.groupby("stop_name")["bus_id"]
                .nunique()
                .loc[lambda s: s > 1]
                .index
                .tolist()
            )
            print(f"\nStart stops: {len(start_stops)} {sorted(start_stops)}")
            print(f"Transfer stops: {len(transfer_stops)} {sorted(transfer_stops)}")
            print(f"Finish stops: {len(finish_stops)} {sorted(finish_stops)}")


    def field_validation(self):
        # parse JSON into list
        bus_data = json.loads(self.buses_and_stops)

        # The 'rules' to validate against
        schema = {
            "bus_id": {"required": True, "type": "integer"},
            "stop_id": {"required": True, "type": "integer"},
            "stop_name": {
                "required": True,
                "type": "string",
                # One or more Proper case words followed by a discreet suffix
                "format": r'^(?:[A-Z][a-zA-Z]*\s)+(?:Road|Avenue|Boulevard|Street)$',
            },
            "next_stop": {"required": True, "type": "integer"},
            "stop_type": {
                "required": False,
                "type": "char",
                "format": r'^[SOF]$',
            },
            "a_time": {
                "required": True,
                "type": "string",
                # Military time format
                "format": r'^(?:[01]\d|2[0-3]):[0-5]\d$',
            },
        }

        error_counts = {field: 0 for field in schema}

        for bus_stop_bus in bus_data:
            self._check_required_fields(bus_stop_bus, schema, error_counts)
            self._check_types(bus_stop_bus, schema, error_counts)
            self._check_formats(bus_stop_bus, schema, error_counts)

        return {
            field: {
                "Required": rules["required"],
                "Type": rules["type"],
                "error_count": error_counts[field],
            }
            for field, rules in schema.items()
        }

    def _check_required_fields(self, bus_stop_bus, schema, error_counts):
        for field, rules in schema.items():
            if rules["required"] and field not in bus_stop_bus:
                error_counts[field] += 1

    def _check_types(self, bus_stop_bus, schema, error_counts):
        for field, rules in schema.items():
            # Avoid double counting error if both required and type checks fail
            if field not in bus_stop_bus:
                continue

            value = bus_stop_bus[field]
            expected_type = rules["type"]

            if expected_type == "integer" and not isinstance(value, int):
                error_counts[field] += 1
            # Must be a non zero length string (value is truthy / falsy)
            elif expected_type == "string" and (not isinstance(value, str) or not value):
                error_counts[field] += 1
            # The one char field in the schema is not required so can be zero length
            elif expected_type == "char" and not is_char(value):
                error_counts[field] += 1

    def _check_formats(self, bus_stop_bus, schema, error_counts):
        for field, rules in schema.items():
            # Avoid double counting error if both required and format checks fail
            if field not in bus_stop_bus or "format" not in rules:
                continue

            value = bus_stop_bus[field]
            # If the value is a non-zero length string, then check if it matches the regex
            if isinstance(value, str) and value and not re.match(rules["format"], value):
                error_counts[field] += 1

    def print_validation_errors(self, validation_results):
        total_errors = sum(errors['error_count'] for field, errors in validation_results.items())
        print(f"Type and field validation: {total_errors} errors")
        for field, errors in validation_results.items():
            print(f"{field}: {errors['error_count']}")

def is_char(x):
    # A valid "char" is either an empty string or a single-character string.
    return isinstance(x, str) and len(x) <= 1

def main():
    input_data = input()
    easy_rider = EasyRider(input_data)
    easy_rider.run()



if __name__ == '__main__':
    main()
