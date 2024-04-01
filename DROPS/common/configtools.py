import yaml

def read_config_file(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

# Example usage
if __name__ == "__main__":
    file_path = "./node.yaml"
    config = read_config_file(file_path)
    print(config)

