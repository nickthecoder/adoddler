from adoddler import configuration
from adoddler.action import AbstractAction

class HTMLTemplateAction( AbstractAction ) :

    def __init__( self, template_name, cache_template = False ) :
        self.template_name = template_name
        if cache_template :
            self.template = configuration.jenv.get_template(template_name)
        else :
            self.template = None

    def default_data( self, handler ) :
        result = dict()
        result[ "params" ] = handler.parameters
        result[ "config" ] = configuration
        result[ "pm" ] = configuration.printer_manager
        result[ "handler" ] = handler
        return result

    def get_GET( self, handler ) :
        template = self.template
        if not template :
            template = configuration.jenv.get_template( self.template_name )
    
        data = self.data_GET( handler )
        data.update( self.default_data( handler ) )
        return template.render( data ).encode("utf-8")

    def get_POST( self, handler ) :
        template = self.template
        if not template :
            template = configuration.jenv.get_template( self.template_name )
    
        data = self.data_POST( handler )
        data.update( self.default_data( handler ) )
        return template.render( data ).encode("utf-8")


    def data_GET( self, handler ) :
        return dict()

    def data_POST( self, handler ) :
        raise Exception( "POST not supported" )

