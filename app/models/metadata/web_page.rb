module Metadata
	class WebPage < Base

		def initialize( name, content, last_update_type )
			super()

			@base['name'] = name
			@base['description'] = content
			@base['dateModified'] = Misc::LastUpdate.where( update_type: last_update_type ).first&.updated_at if last_update_type

		end
	end
end