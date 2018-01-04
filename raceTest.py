import sys
import httplib
import time
import uuid
from urlparse import urlparse


if len(sys.argv) < 2:
    print 'Please provide an xUpload URL'

xUploadRawUrl = sys.argv[1]
xUploadUrl = urlparse(xUploadRawUrl)
xUploadNetloc = xUploadUrl.netloc
query = xUploadUrl.query

if "uuid=" not in xUploadUrl.query:
    if query != "":
        query += '&'
    query += 'uuid=' + str(uuid.uuid1()).replace('-', '')

xUploadQuery = xUploadUrl.path + "?" + query

print 'xUploadNetLoc => ' + xUploadNetloc
print 'xUploadQuery => ' + xUploadQuery

data = '0123456789abcdefghijklmnopqrstuvwxyz'
contentType = 'text/plain'
contentDisposition = 'attachment; filename="file.txt"'
fullContentLength = 36


def format_range(start, end):
    return 'bytes ' + str(start) + '-' + str(end - 1) + '/' + str(fullContentLength)


def parse_offset(response):
    h_range = response.getheader('Range', '0-0/0')
    h_offset = int(h_range[h_range.find('-')+1:h_range.find('/')])
    return 0 if h_offset == 0 else h_offset + 1


def request_offset():
    conn = httplib.HTTPConnection(xUploadNetloc)
    conn.putrequest("POST", xUploadQuery)
    conn.putheader('Content-Type', contentType)
    conn.putheader('Content-Length', 1)
    conn.putheader('Content-Disposition', contentDisposition)
    conn.putheader('Content-Range', format_range(1, 2))
    conn.endheaders()
    conn.send(' ')
    resp = conn.getresponse()
    print 'Request offset Response:', resp.status, resp.reason, parse_offset(resp), resp.read()
    conn.close()
    return parse_offset(resp)


# Send 10 bytes
offset = 0
conn1 = httplib.HTTPConnection(xUploadNetloc)
conn1.putrequest("POST", xUploadQuery)
conn1.putheader('Content-Type', contentType)
conn1.putheader('Content-Length', 10)
conn1.putheader('Content-Disposition', contentDisposition)
conn1.putheader('Content-Range', format_range(offset, offset+10))
conn1.endheaders()
conn1.send(data[0:8])

# Simulate connection failure... We actually sent only 8/10 bytes

# We are lost client side! No problemo. Request the next offset and send 10 bytes
offset = request_offset()
conn2 = httplib.HTTPConnection(xUploadNetloc)
conn2.putrequest("POST", xUploadQuery)
conn2.putheader('Content-Type', contentType)
conn2.putheader('Content-Length', 10)
conn2.putheader('Content-Disposition', contentDisposition)
conn2.putheader('Content-Range', format_range(offset, offset+10))
conn2.endheaders()
conn2.send(data[offset:offset+10])
resp2 = conn2.getresponse()
print 'Request 2 Response:', resp2.status, resp2.reason, parse_offset(resp2), resp2.read()
conn2.close()

# Explicitly close the first failed connection (IRL: should be timouted server-side)
conn1.close()
time.sleep(3)  # Sleep a bit to be sure that everything is closed server-side

# Request the next offset and send the rest of the file
offset = request_offset()
conn3 = httplib.HTTPConnection(xUploadNetloc)
conn3.putrequest("POST", xUploadQuery)
conn3.putheader('Content-Type', contentType)
conn3.putheader('Content-Length', fullContentLength - offset)
conn3.putheader('Content-Disposition', contentDisposition)
conn3.putheader('Content-Range', format_range(offset, fullContentLength))
conn3.endheaders()
conn3.send(data[offset:fullContentLength])
resp3 = conn3.getresponse()
print 'Request 3 Response:', resp3.status, resp3.reason, parse_offset(resp3), resp3.read()
conn3.close()
