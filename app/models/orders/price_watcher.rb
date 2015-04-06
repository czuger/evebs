require 'open-uri'
require 'pp'

class Orders::PriceWatcher
  EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'
  def self.do( item_id, system_id )
    # Refresh the eve central API cache each half hour
    if File.exist?( EVE_CENTRAL_FILE_NAME ) && Time.now - File.ctime( EVE_CENTRAL_FILE_NAME ) > (3600/2)
      `rm -r tmp/api.eve-central.com`
    end
    html_req = "http://api.eve-central.com/api/quicklook?typeid=#{item_id}&usesystem=#{system_id}"
    # pp html_req
    xml_result = open( html_req ).read
    dom = Nokogiri::XML( xml_result )
    price_page =  dom.xpath("//sell_orders//price")
    min = price_page.map{|e| e.children[0].to_s.to_i}.min
    min ? min : 1200 # If there is no sell order, then : 1200
  end
end