def remove_text_before_string(text, target_string):
    # Method 1: Using string split
    if target_string in text:
        return text.split(target_string, 1)[1]
    return text

def remove_text_before_string_regex(text, target_string):
    # Method 2: Using regex
    import re
    pattern = f".*?{re.escape(target_string)}"
    return re.sub(pattern, '', text, 1)

def remove_text_before_string_find(text, target_string):
    # Method 3: Using string find
    index = text.find(target_string)
    if index != -1:
        return text[index:]
    return text

# Example usage
if __name__ == "__main__":
    # Example text
    sample_text = "Hello, this is some text before the target and this is after"
    target = "target"
    
    # Test all methods
    print("Original text:", sample_text)
    print("\nMethod 1 (split):", remove_text_before_string(sample_text, target))
    print("Method 2 (regex):", remove_text_before_string_regex(sample_text, target))
    print("Method 3 (find):", remove_text_before_string_find(sample_text, target)) 