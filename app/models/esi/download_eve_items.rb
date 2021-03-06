class Esi::DownloadEveItems < Esi::Download

  def download

    Misc::Banner.p 'About to download eve items'

    type_ids_to_download = YAML::load_file('data/type_ids_to_download.yaml')
    types = {}

    if @verbose_output
      puts "#{type_ids_to_download.count} types to check."
      check_count = 0
    end

    type_ids_to_download.each do |t|
      @rest_url = "universe/types/#{t}/"

      begin
        type_remote_data = get_page

      rescue Esi::Errors::NotFound
        puts "Data not found for type id : #{t}"
        next
      end

      if @verbose_output
        check_count += 1
        puts "#{check_count} types checked" if check_count % 100 == 0
      end

      next unless type_remote_data['published'] && type_remote_data['market_group_id']

      @rest_url = "universe/types/#{t}/"

      # check for meta level
      meta_level = type_remote_data['dogma_attributes']&.select{ |e| e['attribute_id'] == 633 }&.first
      meta_level = meta_level['value'] if meta_level

      types[t] = { cpp_eve_item_id: t, name: type_remote_data['name'],
                   market_group_id: type_remote_data['market_group_id'], volume: type_remote_data['volume'],
                   mass: type_remote_data['mass'], icon_id: type_remote_data['icon_id'], desc: type_remote_data['description'],
                   packaged_volume: type_remote_data['packaged_volume'], meta_level: meta_level }
    end

    File.open('data/types.yaml', 'w') {|f| f.write types.to_yaml }

  end
end