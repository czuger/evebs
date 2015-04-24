class MultipleMinPriceRetriever

  include MinPriceRetriever

  def self.get_min_prices( system_id, item_ids )
    # Refresh the eve central API cache each 4 hours
    if File.exist?( EVE_CENTRAL_FILE_NAME ) && Time.now - File.ctime( EVE_CENTRAL_FILE_NAME ) > (3600*4)
      `rm -r tmp/api.eve-central.com`
    end
    final_hash = {}
    item_ids.each_slice(200) do |id_slice|
      html_req = "http://api.eve-central.com/api/marketstat/json?typeid=#{id_slice.join(',')}&usesystem=#{system_id}"
      json_result = open( html_req ).read
      parsed_data = JSON.parse( json_result ).map{ |e| [ e['sell']['forQuery']['types'].first, (e['sell'][ 'min' ]<=0 ? nil : e['sell'][ 'min' ]) ] }
      final_hash.merge!( Hash[ parsed_data ] )
    end
    final_hash
  end

end