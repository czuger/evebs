module Modules::PriceAdvices::ShowItemDetail

  def show
    @item = EveItem.find( params[ :id ] )

    current_min_price_hash = {}
    current_min_prices = MinPrice.where( eve_item_id: @item.id )
    current_min_price_hash = Hash[ current_min_prices.map{ |e| [ e.trade_hub_id, e.min_price ] } ] if current_min_prices

    avg_prices_hash = {}
    last_month_averages = CrestPricesLastMonthAverage.where( eve_item_id: @item.id )
    if last_month_averages
      last_month_averages.each do |last_month_average|
        last_month_average.region.trade_hub_ids.each do |trade_hub_id|
          avg_prices_hash[trade_hub_id] = last_month_average
        end
      end
    end

    # TODO : create a super regroupment on the region in order to regroup all region linked rows (with rowspan)
    @item_cost = @item.single_unit_cost
    trade_hubs_ids = (current_min_price_hash.keys + avg_prices_hash.keys).uniq

    @region_array = {}

    TradeHub.where( id: trade_hubs_ids ).order( :name ).each do |trade_hub|

      unless @region_array.has_key?( trade_hub.region_id )

        avg_price = avg_prices_hash[trade_hub.id].avg_price_avg if avg_prices_hash[trade_hub.id]
        volume = (avg_prices_hash[trade_hub.id].volume_sum if avg_prices_hash[trade_hub.id])

        @region_array[ trade_hub.region_id ] = {
          region_data: {
            avg_price_margin: @item.pcent_margin( avg_price ),
            avg_price: avg_price,
            volume: volume
          },
          trades_hubs_data: []
        }
      end

      @region_array[ trade_hub.region_id ][ :trades_hubs_data ] << {
        trade_hub: trade_hub.name,
        min_price_margin: @item.pcent_margin( current_min_price_hash[trade_hub.id] ),
        min_price: current_min_price_hash[trade_hub.id],
      }

    end

    @region_array_sorted_keys = @region_array.map{ |e| [ e[1][:region_data][:volume], e[0] ] }
    @region_array_sorted_keys.sort_by!{ |e| nvl( e[ 0 ] ) }
    @region_array_sorted_keys.reverse!

  end

end