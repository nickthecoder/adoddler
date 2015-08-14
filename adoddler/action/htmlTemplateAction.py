from adoddler import configuration
from adoddler.action import AbstractAction
from adoddler.printer import PrinterStatus, JobStatus

class HTMLTemplateAction( AbstractAction ) :

    def __init__( self, template_name ) :
        self.template_name = template_name
        if configuration.cache_templates :
            self.template = configuration.jenv.get_template(template_name)
        else :
            self.template = None

    def default_data( self, handler ) :
        return {
            "params": handler.parameters,
            "config": configuration,
            "pm": configuration.printer_manager,
            "handler": handler,
            "job": configuration.printer_manager.print_job,
            "PrinterStatus" : PrinterStatus,
            "JobStatus" : JobStatus
            }

    def get_GET( self, handler ) :
        # Get the template if it wasn't cached in the constructor
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

