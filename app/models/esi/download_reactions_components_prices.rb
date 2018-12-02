class Esi::DownloadReactionsComponentsPrices < Esi::Download

  def download

    types = [ 16642, 4246, 16635, 16636, 16656, 16660, 16672, 16673, 16639, 16638, 16641,
              16654, 16658, 16671, 4312, 16644, 4051, 16634, 16657, 16661, 16637, 16649,
              16662, 16633, 4247, 16659, 16679, 25273, 3645, 25242, 25268, 25237, 16640,
              16643, 16655, 16670, 16647, 16663, 16648, 17959, 16680 ]

    Misc::Banner.p 'About to download reactions components prices'

    results = []

    types.each do |t|
      @rest_url = "universe/types/#{t}/"

      begin
        type_remote_data = get_page

      rescue Esi::Errors::NotFound
        puts "Data not found for type id : #{t}"
        next
      end

      type_data = { type_id: t, name: type_remote_data['name'] }

      @rest_url = "markets/10000002/orders/"
      @params= { order_type: :sell, type_id: t }

      begin
        type_remote_datas = get_all_pages

      rescue Esi::Errors::NotFound
        puts "Data not found for type id : #{t}"
        next
      end

      type_remote_datas.reject!{ |e| e['system_id'] != 30000142 }
      min_price = min_price = type_remote_datas.map{ |e| e['price'] }.min

      # pp type_remote_datas

      type_data[:min_price] = min_price

      results << type_data
    end

    # pp results
    # File.open('data/reactions_components_prices.yaml', 'w') {|f| f.write types.to_yaml }

    results << { name: 'ZZZZZZZZZZZ', min_price: -999999 }
    results.sort_by!{ |e| e[:name] }

    results.each do |e|
      next unless e[:min_price]
      puts "#{e[:name]}\t#{e[:min_price].round}"
    end
  end
end