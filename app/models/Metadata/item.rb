module Metadata
	class Item < Base

		def to_json( item, item_url )
			@base['@type'] = 'ItemPage'
			@base['name'] = item.name
			@base['description'] = item.description.truncate_words( 100 )
			@base['url'] = item_url
			@base['lastReviewed'] = Misc::LastUpdate.where( update_type: :daily ).first&.updated_at

			@base.to_json
		end

	end
end

