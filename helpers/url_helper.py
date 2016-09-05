
def build_url(base_url, path, method=None):
    sub_path = "/".join(path)
    if method == 'POST':
        return base_url + sub_path + '/'
    return base_url + sub_path
