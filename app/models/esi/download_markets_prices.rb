require_relative 'download'

class Esi::DownloadMarketsPrices < Download

  def initialize( debug_request: false )
    super( 'markets/prices/', {}, debug_request: debug_request )
  end

  def fill_table
    records = []
    get_page.each do |record|
      records << EveMarketsPrice.new(
          type_id: record['type_id'], average_price: record['average_price'], adjusted_price: record['adjusted_price'] )
    end
    EveMarketsPrice.delete_all
    EveMarketsPrice.import( records )
  end

end