import json

class EasyRider:
    def __init__(self, buses_and_stops):
        self.buses_and_stops = buses_and_stops

    def run(self):
        validation_results = self.field_validation()
        self.print_validation_errors(validation_results)


    def field_validation(self):
        bus_data = json.loads(self.buses_and_stops)
        schema_error_check = {
            "bus_id": {"Required": True, "Type": "integer", "error_count": 0 }, # required, type, error_count, length
            "stop_id": {"Required": True, "Type": "integer", "error_count": 0 },
            "stop_name": {"Required": True, "Type": "string", "error_count": 0 },
            "next_stop": {"Required": True, "Type": "integer", "error_count": 0 },
            "stop_type": {"Required": False, "Type": "char", "error_count": 0 },
            "a_time": {"Required": True, "Type": "string", "error_count": 0 }
        }
        for bus_stop_bus in bus_data:
            # Check for missing required fields
            for field, rules in schema_error_check.items():
                if field not in bus_stop_bus:
                    if rules["Required"]:
                        rules["error_count"] += 1
                    continue

            # Check for incorrect data types
                if rules["Type"] == "integer" and not isinstance(bus_stop_bus[field], int):
                    rules["error_count"] += 1
                elif rules["Type"] == "string":
                    if not isinstance(bus_stop_bus[field], str) or len(bus_stop_bus[field]) == 0:
                        rules["error_count"] += 1
                if rules["Type"] == "char" and not is_char(bus_stop_bus[field]):
                    rules["error_count"] += 1

        return schema_error_check

    def print_validation_errors(self, validation_results):
        total_errors = sum(errors['error_count'] for field, errors in validation_results.items())
        print(f"Type and field validation: {total_errors} errors")
        for field, errors in validation_results.items():
            print(f"{field}: {errors['error_count']}")

def is_char(x):
    return isinstance(x, str) and len(x) <= 1

def main():
    input_data = input()
    easy_rider = EasyRider(input_data)
    easy_rider.run()



if __name__ == '__main__':
    main()
