from java.io import *
from java.net import *
from java.lang import *

import sys, os
import jarray

# WEB_ROOT is the directory where our HTML and other files reside.
# For this package, WEB_ROOT is the "webroot" directory under the working
# directory.
# The working directory is the location in the file system
# from where the java command was invoked.
#WEB_ROOT = os.getcwd() + File.separator + 'webroot'
#WEB_ROOT = '~/tmp/webroot'
WEB_ROOT = '/Users/adharmad/tmp/webroot'

SHUTDOWN_COMMAND = '/SHUTDOWN'
PORT = 8080
LOCALHOST = '127.0.0.1'

class Request:
    def __init__(self, input=None):
        self.input = input
        self.uri = ''

    def parse(self):
        request = ''
        buffer = jarray.zeros(2048, 'b')
        charsRead = 0

        try:
            charsRead = self.input.read(buffer)
        except IOException as ioex:
            ioex.printStackTrace()
            charsRead = -1

        request = buffer.tostring()

        print("Request is\n")
        print(request)
        self.uri = self.parseUri(request)
        print("URI is ", self.uri)

    def parseUri(self, reqStr):
        try:
            idx1 = reqStr.index(' ')
            idx2 = reqStr.index(' ', idx1+1)
            return reqStr[idx1+1:idx2]
        except ValueError as ve:
            return None

# HTTP Response = Status-Line
#   *(( general-header | response-header | entity-header ) CRLF)
#   CRLF
#   [ message-body ]
#   Status-Line = HTTP-Version SP Status-Code SP Reason-Phrase CRLF
class Response:

    ERRORMESSAGE = """
    HTTP/1.1 404 File Not Found\r\n
    Content-Type: text/html\r\n
    Content-Length: 23\r\n\r\n
    <h1>File Not Found</h1>
    """
    def __init__(self, out):
        self.request = None
        self.out = out

    def sendStaticResource(self):
        try:
            f = open(WEB_ROOT + self.request.uri, 'r')
            lines = f.readlines()
            content = ''
            for line in lines:
                content += line
            f.close()
            self.out.write(content)
        except IOError as ioerr:
            pass

    def sendErrorMessage(self):
        self.out.write(self.ERRORMESSAGE)

class HttpServer:
    def __init__(self):
        self.shutdown = False

    def await(self):
        serverSocket = None
        try:
            serverSocket = ServerSocket(PORT, 1,
                    InetAddress.getByName(LOCALHOST))
        except IOException as ioex:
            ioex.printStackTrace()
            sys.exit(1)

        while not self.shutdown:
            socket = None
            input = None
            output = None

            print 'In server main loop'
            
            try:
                socket = serverSocket.accept()
                input = socket.getInputStream()
                output = socket.getOutputStream()

                # create Request object and parse
                request = Request(input)
                request.parse()

                # create Response object
                response = Response(output)
                response.request = request
                response.sendStaticResource()

                # Close the socket
                socket.close()

                # check if the previous URI is a shutdown command
                self.shutdown = request.uri == SHUTDOWN_COMMAND

            #except IOError as ioerr:
            #    print(ioerr)

            #except Exception as ex:
            #    ex.printStackTrace()
            except:
                print("---------------------")
                response.sendErrorMessage()

# Entry point
if __name__ == '__main__':
    server = HttpServer()
    server.await()
