module Metadata
	class Base

		def initialize( last_update_type= nil )
			@audience = {
				'@type' => 'PeopleAudience',
				suggestedGender: :male,
				suggestedMaxAge: 19,
				suggestedMinAge: 46,
				audienceType: 'videogames players'
			}

			@about = {
				'@type' => 'VideoGame',
				name: 'Eve Online',
				url: 'https://www.eveonline.com/',
				operatingSystem: 'Windows 7 Service Pack 1, Mac OS X 10.12',
				applicationCategory: 'massively multiplayer online role-playing game'
			}

			@base = { '@context' => 'http://schema.org', '@type' => 'WebPage' }
			@base['Audience'] = @audience
			@base['about'] = @about

			set_expires( last_update_type )
		end

		def to_json
			@base.to_json
		end

		def add_breadcrumb( breadcrumb )
			bc = {
				'@type' => 'BreadcrumbList',
				'itemListElement' => breadcrumb.each_with_index.map{ |e, i|
					{
						'@type': 'ListItem',
						'position': i+1,
						'name': e.name,
						item: e.url
					}
				}
			}

			@base['breadcrumb'] = bc
		end

		private

		def set_expires( last_update_type )
			if last_update_type
				modified_date = Misc::LastUpdate.where( update_type: last_update_type ).first&.updated_at
				@base['dateModified'] = modified_date

				expiry_date = DateTime.now.at_end_of_week + 4.hours
				expiry_date = DateTime.now.at_end_of_day + 4.hours if last_update_type == :daily
				expiry_date = DateTime.now.at_end_of_hour + 30.minutes if last_update_type == :hourly

				@base['expires'] = expiry_date
			end

		end
	end
end