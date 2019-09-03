module Metadata
	class Base

		def initialize( breadcrumb: nil )
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
				operatingSystem: 'Windows, OSX, Linux',
				applicationCategory: 'massively multiplayer online role-playing game'
			}

			@base = { '@context' => 'http://schema.org' }
			@base['Audience'] = @audience
			@base['about'] = @about

			@base['BreadcrumbList'] = @breadcrumb if @breadcrumb
		end

		private

		def set_breadcrumb( breadcrumb )
			if breadcrumb
				@breadcrumb = {
					breadcrumb: {
						'@type' => 'BreadcrumbList',
						'itemListElement' => breadcrumb.each_with_index.map{ |e, i|
							{
								'@type': 'ListItem',
								'position': i,
								'item':
									{
										'@id': e.id, # all_items_list_list_items_url( group_id: e.id ),
										'name': e.name
									}
							}
						}
					}
				}
			end
		end

	end
end