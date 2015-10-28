module MultiplePriceRetriever

  EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'

  def get_prices( eve_system_id, item_ids, price_kind = 'min' )

    # Refresh the eve central API cache each 1 hours
    if File.exist?( EVE_CENTRAL_FILE_NAME ) && Time.now - File.ctime( EVE_CENTRAL_FILE_NAME ) >= (3600-(60*5))
      `rm -r tmp/api.eve-central.com`
    end

    final_hash = {}
    item_ids.each_slice(200) do |id_slice|
      html_req = "http://api.eve-central.com/api/marketstat/json?typeid=#{id_slice.join(',')}&usesystem=#{eve_system_id}"
      # puts html_req

      begin
        json_result = open( html_req ).read
      rescue StandardError => e
        puts '*'*200
        puts 'Error !!!'
        puts '*'*200
        puts "Caught in MultiplePriceRetriever##{__method__} at #{Time.now}"
        puts
        puts e.message
        puts
        puts e.backtrace
        puts '*'*200
        puts 'End of error desc'
        puts '*'*200
        exit
      end

      parsed_data = JSON.parse( json_result ).map{ |e| [ e['sell']['forQuery']['types'].first, (e['sell'][ price_kind ]<=0 ? nil : e['sell'][ price_kind ]) ] }
      final_hash.merge!( Hash[ parsed_data ] )
    end
    final_hash

  end

end