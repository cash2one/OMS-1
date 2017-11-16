

def validate_address(self, raw_address):
    keys_zh = r'[^\u4e00-\u9fa5^A-Za-z_0-9,\,\:\.\x00,\，\：\ \。\#]'
    if (raw_address == ""):
        return False
    return True
