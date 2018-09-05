class Esi::UpdateMarketGroups < Esi::Download

  def initialize( debug_request: false )
    super( 'markets/groups/', {}, debug_request: debug_request )
  end

  def update
    Banner.p 'About to update market groups'

    groups_updated = 0
    groups_created = 0
    market_groups = get_all_pages.to_a
    # pp market_groups

    ActiveRecord::Base.transaction do

      Banner.p 'About to download market groups data'

      market_groups.each do |mg|
        @rest_url = "markets/groups/#{mg}"

        get_all_pages.each do |group_info|
          # p group_info
          group_created = false
          group = MarketGroup.where( cpp_market_group_id: group_info['market_group_id'] ).first_or_initialize do
            group_created = true
            groups_created += 1
          end

          group.name = group_info['name']
          group.cpp_parent_market_group_id = group_info['parent_group_id']

          group.save!
          groups_updated += 1 unless group_created

          unless group_info['types'].empty?
            EveItem.where( cpp_eve_item_id: group_info['types'] ).update_all( market_group_id: group.id )
          end
        end
      end

      Banner.p 'About to update market groups hierarchy'
      MarketGroup.all.each do |mg|
        mg.parent_id = MarketGroup.find_by_cpp_market_group_id( mg.cpp_parent_market_group_id )&.id
        begin
          mg.save
        rescue => e
          p e
          raise e
        end

      end
    end

    puts "#{groups_updated} groups updated #{groups_created} groups created"

  end
end