module Misc
	class BreadcrumbSubItem

		def initialize( name, url, parent_item, view_context )
			@name = name
			@url = url
			@parent_item = parent_item
			@view_context = view_context
		end

		def breadcrumb
			bc = @parent_item.breadcrumb( @view_context )
			bc << Misc::BreadcrumbElement.new( @name, @url )
		end

	end
end
