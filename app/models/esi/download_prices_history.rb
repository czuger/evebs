require_relative 'download'

class Esi::DownloadPricesHistory < Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    p @errors_limit_remain
  end

  def update_table

    items = EveItem.pluck( :id, :cpp_eve_item_id )
    regions = Region.pluck( :id, :cpp_region_id )

    regions.each do |region|
      internal_region_id, cpp_region_id = region
      cpp_region_id = cpp_region_id.to_i

      items.each do |item|
        internal_eve_item_id, cpp_eve_item_id = item

        next if empty_history?( cpp_region_id, cpp_eve_item_id )

        @rest_url = "markets/#{cpp_region_id}/history/"
        @params[:type_id]=cpp_eve_item_id
        pages = get_page

        if pages.empty?
          set_empty_history( cpp_region_id, cpp_eve_item_id )
          next
        end

        timestamps = pages.map{ |r| timestamp( r ) }

        downloaded_timestamps = EveMarketsHistory.where(
            region_id: internal_region_id, eve_item_id: internal_eve_item_id ).where( day_timestamp: timestamps ).
            pluck( :day_timestamp )

        downloaded_timestamps = downloaded_timestamps.to_set

        records = []
        pages.each do |record|
          next if downloaded_timestamps.include?( timestamp( record ) )

          record = EveMarketsHistory.new(
              region_id: cpp_region_id, eve_item_id: cpp_eve_item_id, day_timestamp: timestamp( record ),
              history_date: DateTime.parse( record['date'] ), order_count: record['order_count'], volume: record['volume'],
              low_price: record['lowest'], avg_price: record['average'], high_price: record['highest'] )

          puts 'Inserting' if @debug_request
          p record if @debug_request
        end
        EveMarketsHistory.import( records )
      end
    end

  end

  private

  def set_empty_history( cpp_region_id, cpp_eve_item_id )
    # Don't forget to clean up old markets to give a chance to refresh it.
    EveEmptyMarketHistory.create!( cpp_region_id: cpp_region_id, cpp_eve_item_id: cpp_eve_item_id )
  end

  def empty_history?( cpp_region_id, cpp_eve_item_id )
    # Initializing empty history
    unless @empty_history
      @empty_history = EveEmptyMarketHistory.pluck( :cpp_region_id, :cpp_eve_item_id )
      @empty_history = @empty_history.to_set
    end

    @empty_history.include?( [ cpp_region_id, cpp_eve_item_id ] )
  end

  def timestamp( record )
    record['date'].delete( '-' )
  end

end