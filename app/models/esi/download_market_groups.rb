class Esi::DownloadMarketGroups < Esi::Download

  def download
    Misc::Banner.p 'About to download market groups'

    types = YAML::load_file('data/types.yaml')

    # Remove the compact order once the item without market id are removed.
    market_group_ids = types.values.select{ |t| t[:base_item] == false }.map{ |t| t[:market_group_id] }.uniq.compact
    @market_groups_hash = {}

    if @verbose_output
      puts "#{market_group_ids.count} market groups to check."
      check_count = 0
    end

    market_group_ids.each do |m_id|

      download_market_group_id( m_id )

      if @verbose_output
        check_count += 1
        puts "#{check_count} markets checked" if check_count % 100 == 0
      end

    end

    File.open('data/market_groups.yaml', 'w') {|f| f.write @market_groups_hash.to_yaml }

  end

  def download_market_group_id( m_id )

    @rest_url = "markets/groups/#{m_id}"

    begin
      market_data = get_page( 1 )
    rescue Esi::Errors::NotFound
      puts "Data not found for market id : #{t}"
      return
    end

    if market_data['name'] && !market_data['name'].empty?
      @market_groups_hash[m_id] = { market_group_id: market_data['market_group_id'], name: market_data['name'],
                                    parent_group_id: market_data['parent_group_id'] }

      if market_data['parent_group_id'] && !@market_groups_hash[ market_data['parent_group_id'] ]
        download_market_group_id( market_data['parent_group_id'] )
      end
    else
      puts 'Bad market data found'
      pp market_data
    end
  end
end