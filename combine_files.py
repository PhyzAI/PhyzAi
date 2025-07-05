def combine_files(file1_path, file2_path, output_path):
    try:
        # Read first file
        with open(file1_path, 'r', encoding='utf-8') as file1:
            content1 = file1.read()
        
        # Read second file
        with open(file2_path, 'r', encoding='utf-8') as file2:
            content2 = file2.read()
        
        # Combine the contents with quotes
        combined_content = '"' + content1 + "\n" + content2 + '"'
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(combined_content)
            
        print(f"Successfully combined files into {output_path}")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find one of the files - {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # Example file paths
    file1 = "first_file.txt"
    file2 = "second_file.txt"
    output = "combined_output.txt"
    
    # Combine the files
    combine_files(file1, file2, output) 