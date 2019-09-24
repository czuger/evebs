# Set the host name for URL creation
SitemapGenerator::Sitemap.default_host = 'https://evebs.ieroe.com'

ITEMS_PRIORITIES = {
	'Drones' => 1,
	'Ship Equipment' => 0.8,
	'Manufacture & Research' => 0.7,
	'Ship and Module Modifications' => 0.1,
	'Ammunition & Charges' => 1,
	'Structures' => 0.2,
	'Trade Goods' => 0,
	'Special Edition Assets' => 0,
	'Implants & Boosters' => 0.1,
	'Ships' => 0.8,
	'Structure Equipment' => 0.2,
	'Structure Modifications' => 0.2,
	'Planetary Infrastructure' => 0.3
}
SitemapGenerator::Sitemap.create do

  @jita = TradeHub.find_by_eve_system_id(30000142)

	add root_path, :priority => 1.0

  EveItem.find_each do |item|
    unless item.base_item || !item.blueprint
			# Only produced items will be in the sitemap (cost of tritanium has no interest)

			market_root_name = item.market_group&.root&.name
			priority = ITEMS_PRIORITIES[market_root_name] || 0

			add item_path(item), changefreq: :weekly, :lastmod => Misc::LastUpdate.find_by( update_type: 'weekly' ).updated_at, priority: priority

			add market_data_market_overview_path(item), changefreq: :hourly, :lastmod => Misc::LastUpdate.find_by( update_type: 'hourly' ).updated_at,
					priority: [ priority-0.1 ,0 ].max

			add production_cost_market_histories_path(item), changefreq: :daily, :lastmod => Misc::LastUpdate.find_by( update_type: 'daily' ).updated_at,
					priority: [ priority-0.2 ,0 ].max

			add production_cost_path(item), changefreq: :daily, :lastmod => Misc::LastUpdate.find_by( update_type: 'daily' ).updated_at,
					priority: [ priority-0.3 ,0 ].max
    end
  end

  # Put links creation logic here.
  #
  # The root path '/' and sitemap index file are added automatically for you.
  # Links are added to the Sitemap in the order they are specified.
  #
  # Usage: add(path, options={})
  #        (default options are used if you don't specify)
  #
  # Defaults: :priority => 0.5, :changefreq => 'weekly',
  #           :lastmod => Time.now, :host => default_host
  #
  # Examples:
  #
  # Add '/articles'
  #
  #   add articles_path, :priority => 0.7, :changefreq => 'daily'
  #
  # Add all articles:
  #
  #   Article.find_each do |article|
  #     add article_path(article), :lastmod => article.updated_at
  #   end
end
