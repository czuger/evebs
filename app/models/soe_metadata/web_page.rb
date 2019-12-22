module SoeMetadata
	class WebPage < Base

		def initialize( name, content, last_update_type )
			super( last_update_type )

			@base['name'] = name
			@base['description'] = content

		end
	end
end