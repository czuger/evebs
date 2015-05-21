require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

module MinPriceRetriever
  EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'
  def get_min_price_from_eve_central( item_id, system_id )
    # Refresh the eve central API cache each 4 hours
    if File.exist?( EVE_CENTRAL_FILE_NAME ) && Time.now - File.ctime( EVE_CENTRAL_FILE_NAME ) > (3600*4)
      `rm -r tmp/api.eve-central.com`
    end
    html_req = "http://api.eve-central.com/api/quicklook?typeid=#{item_id}&usesystem=#{system_id}"
    puts "About to request #{html_req}"
    xml_result = open( html_req ).read
    dom = Nokogiri::XML( xml_result )
    price_page =  dom.xpath("//sell_orders//price")
    min = price_page.map{|e| e.children[0].to_s.to_i}.min
  end
end