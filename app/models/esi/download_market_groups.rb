class Esi::DownloadMarketGroups < Esi::Download

  def initialize( debug_request: false )
    super( 'markets/groups/', {}, debug_request: debug_request )
  end

  def update
    puts 'Updating market_groups.'

    groups_updated = 0
    market_groups = get_all_pages.to_a
    # pp market_groups

    market_groups.each do |mg|
      @rest_url = "markets/groups/#{mg}"

      get_all_pages.each do |group_info|
        unless group_info['types'].empty?
          group = MarketGroup.where( cpp_market_group_id: group_info['market_group_id'] ).first_or_initialize do |g|
            g.name = group_info['name']
            g.parent_id = group_info['parent_group_id']
            g.cpp_type_ids = group_info['types']
          end
          group.save!
          groups_updated += 1
        end
      end
    end

    puts "#{groups_updated} groups updated."

  end
end