module Misc
	class BreadcrumbElement

		attr_reader :name, :url

		def initialize( name, url )
			@name = name
			@url = url
		end

		def self.bc_from_sub_item( name, url, parent_item, view_context )
			bc = parent_item.breadcrumb( view_context )
			bc << Misc::BreadcrumbElement.new( name, url )
		end

	end
end