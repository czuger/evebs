module Misc
	class BreadcrumbRoot

		def breadcrumb( view_context )
			[ Misc::BreadcrumbElement.new( 'Items', view_context.list_items_url ) ]
		end

	end
end