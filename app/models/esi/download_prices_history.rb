require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadPricesHistory < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update_table
    Banner.p 'About to update the table eve_markets_histories'

    jita = Region.find_by_cpp_region_id( '10000002' )

    jita.eve_items_in_market.each do |eve_item|

      @rest_url = "markets/#{jita.cpp_region_id}/history/"
      @params[:type_id]=eve_item.cpp_eve_item_id
      pages = get_all_pages

      # pp pages

      timestamps = pages.map{ |r| timestamp( r ) }

      downloaded_timestamps = EveMarketsHistory.where(
          region_id: jita.id, eve_item_id: eve_item.id ).where( day_timestamp: timestamps ).
          pluck( :day_timestamp )

      downloaded_timestamps = downloaded_timestamps.to_set

      records = []
      pages.each do |record|
        next if downloaded_timestamps.include?( timestamp( record ) )

        record = EveMarketsHistory.new(
            region_id: jita.id, eve_item_id: eve_item.id, day_timestamp: timestamp( record ),
            history_date: DateTime.parse( record['date'] ), order_count: record['order_count'], volume: record['volume'],
            low_price: record['lowest'], avg_price: record['average'], high_price: record['highest'] )
        records << record
      end
      EveMarketsHistory.import( records )
      puts "#{records.count} inserted" if @debug_request
    end

  end

  private

  # def set_empty_history( cpp_region_id, cpp_eve_item_id )
  #   # Don't forget to clean up old markets to give a chance to refresh it.
  #   EveEmptyMarketHistory.create!( cpp_region_id: cpp_region_id, cpp_eve_item_id: cpp_eve_item_id )
  # end
  #
  # def empty_history?( cpp_region_id, cpp_eve_item_id )
  #   # Initializing empty history
  #   unless @empty_history
  #     @empty_history = EveEmptyMarketHistory.pluck( :cpp_region_id, :cpp_eve_item_id )
  #     @empty_history = @empty_history.to_set
  #   end
  #
  #   @empty_history.include?( [ cpp_region_id, cpp_eve_item_id ] )
  # end

  def timestamp( record )
    record['date'].delete( '-' )
  end

end