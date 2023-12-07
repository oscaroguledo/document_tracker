import re

def identify_browser(user_agent):
    if re.search(r'Chrome', user_agent):
        return 'Google Chrome'
    elif re.search(r'Safari', user_agent) and re.search(r'AppleWebKit', user_agent):
        return 'Safari'
    elif re.search(r'Firefox', user_agent):
        return 'Mozilla Firefox'
    elif re.search(r'Opera', user_agent):
        return 'Opera'
    elif re.search(r'Edge', user_agent):
        return 'Microsoft Edge'
    elif re.search(r'MSIE', user_agent):
        return 'Internet Explorer'
    else:
        return 'Unknown Browser'

# Example usage:
user_agent_string = "Mozilla/5.0 (Windows NT 6.1; rv:27.0) Gecko/20100101 Firefox/27.0"
browser = identify_browser(user_agent_string)
print(f"The browser used is: {browser}")
