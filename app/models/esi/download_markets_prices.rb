require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadMarketsPrices < Esi::Download

  def initialize( debug_request: false )
    super( 'markets/prices/', {}, debug_request: debug_request )
  end

  def download
    Banner.p 'About to download cpp markets prices'

    File.open( 'data/cpp_market_prices.yaml', 'w' ) do |f|
      f.puts( Hash[ get_all_pages.map{ |e| [ e['type_id'], e ] } ].to_yaml )
    end
  end

end