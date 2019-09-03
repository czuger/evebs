module Metadata
	class Base

		def initialize
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
		end

		def to_json
			@base.to_json
		end

		def add_breadcrumb( breadcrumb )
			if breadcrumb
				bc = {
					'@type' => 'BreadcrumbList',
					'itemListElement' => breadcrumb.each_with_index.map{ |e, i|
						{
							'@type': 'ListItem',
							'position': i+1,
							'name': e.name,
							item: yield( e.group_id )
						}
					}
				}

				@base['breadcrumb'] = bc
			end
		end

	end
end