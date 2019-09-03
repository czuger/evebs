module Metadata
	class WebPage < Base

		def initialize( name, content, last_update_type )
			super()

			@base['name'] = name
			@base['description'] = content

		end
	end
end