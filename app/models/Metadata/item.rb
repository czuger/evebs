module Metadata
	class Item < Base

		def add( item, item_url )
			@base['@type'] = 'ItemPage'
			@base['name'] = item.name
			@base['description'] = item.description.truncate_words( 100 )
			@base['url'] = item_url
		end

	end
end

