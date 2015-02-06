import socket
import sys
import os
import mimetypes

def resolve_uri(uri):
    # Setting up web root
    root = os.path.abspath("webroot")
    f = root + uri
    f = os.path.abspath(f)

    # Checking if paht is a directory, a file, or wrong path
    if os.path.isdir(f):
        content_type = "text/plain"
        rstring = ""
        filelist = os.listdir(f)
        # listing files and directories
        rstring = "<html><body><table border='1' cellpadding='5'>"
        for i in filelist:
            rstring += "<tr>"
            if i.find(".") > -1:
                rstring += "<td>" + mimetypes.guess_type(i)[0] + "</td><td>" + i + "</td>"
            else:
                rstring += "<td>directory</td><td>" + i + "</td>"
            rstring += "</tr>"
        rstring += "</table></body></html>"
        return (rstring, content_type)
    elif os.path.isfile(f):
        content_type = mimetypes.guess_type(f)[0]
        content = ""
        # Displaying content
        with open (f, "rb") as fname:
            content = fname.read()
        return (content, content_type)
    else:
        # Returning error in text/plain
        return(None, None)
 
def response_not_found():
    """ returns a 404 Resource not Found """
    resp = []
    resp.append("HTTP/1.1 404 Resource Not Found")
    resp.append("")
    resp.append("404 Not Found")
    return "\r\n".join(resp)

def response_ok(content, type):
    """returns a basic HTTP response"""
    try: 
        resp = []
        resp.append("HTTP/1.1 200 OK")
        resp.append(type)
        resp.append("")
        resp.append(content)
        return "\r\n".join(resp)
    except TypeError:
        raise NameError("404 Not Found")


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp)

def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri


def server():
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>sys.stderr, "making a server on %s:%s" % address
    sock.bind(address)
    sock.listen(1)
    
    try:
        while True:
            print >>sys.stderr, 'waiting for a connection'
            conn, addr = sock.accept() # blocking
            try:
                print >>sys.stderr, 'connection - %s:%s' % addr
                request = ""
                while True:
                    data = conn.recv(1024)
                    request += data
                    if len(data) < 1024 or not data:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    content, type = resolve_uri(uri) # change this line
                    try:
                        response = response_ok(content, type)
                    except NameError:
                        print "inside error"
                        response = response_not_found()

                print >>sys.stderr, 'sending response'
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
