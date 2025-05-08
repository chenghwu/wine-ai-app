import os

def parse_env_file(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                outfile.write(f'{key.strip()}: "{value.strip()}"\n')

# Example usage
parse_env_file('.env', '.env.yaml')