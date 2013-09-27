from pipes import quote


def request_to_curl_command(req):
    cmd = ["curl", "--verbose"]

    if req.method:
        cmd.extend(["-X", req.method.upper()])

    if req.body:
        cmd.extend(["-d", quote(req.body)])

    if req.headers:
        for (name, value) in req.headers.items():
            cmd.extend(["-H", quote("%s: %s" % (name, value))])

    cmd.append(quote(req.url))

    return " ".join(cmd)
