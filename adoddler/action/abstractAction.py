import urllib
from adoddler import configuration

class AbstractAction :

    def send_redirect(self, handler, url, parameters=None ) :
        if parameters :
            url = url + "?" + urllib.urlencode( parameters )

        handler.send_response(302)
        handler.send_header("Location", url )
        handler.end_headers()

    def get_content_type( self, handler ) :
        return "text/html; charset=UTF-8"

    def send_head(self, handler, text) :
        handler.send_response(200)
        handler.send_header("Content-type", self.get_content_type( handler ) )
        handler.send_header("Content-Length", str(len(text)))


    def do_HEAD(self, handler) :

        text = self.get_GET(handler)
        self.send_head( handler, text )
        handler.end_headers()

    def do_GET(self, handler) :

        text = self.get_GET(handler)
        self.send_head( handler, text )
        handler.end_headers()

        handler.wfile.write( text )

    def do_POST(self, handler) :

        text = self.get_POST(handler)
        self.send_head( handler, text )
        handler.end_headers()

        handler.wfile.write( text )


    def get_GET( self, handler ) :
        raise
    
    def get_POST( self, handler ) :
        raise

