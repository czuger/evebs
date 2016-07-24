module Modules::PriceAdvices::MarginModule

  def advice_prices_margins( margin_type )

    raise "#{self.class}##{__method__} : margin_type can't be nil" unless margin_type

    @user = current_user
    @prices_array = []
    @monthly_averages = get_montly_items_averages
    @shopping_basket = get_shopping_basket

    user_eve_items = @user.eve_items.includes( :blueprint )

    @user.trade_hubs.includes( :region ).each do |trade_hub|

      eve_items = user_eve_items
      if @user.remove_occuped_places
        eve_items = user_eve_items.where.not( id: trade_hub.get_selling_eve_items_ids( @user ) )
      end

      if margin_type == :daily
        min_price_items = MinPrice.where( { eve_item_id: eve_items.pluck( :id ), trade_hub_id: trade_hub.id } )
        min_price_items = Hash[ min_price_items.pluck( :eve_item_id, :min_price ) ]
      end

      eve_items.find_each do |eve_item|

        region_item_key = [[trade_hub.region_id],[eve_item.id]]

        if @monthly_averages && @monthly_averages[region_item_key]
          avg_price = @monthly_averages[region_item_key].avg_price_avg
          volume_sum = @monthly_averages[region_item_key].volume_sum
        end

        if margin_type == :monthly
          price = avg_price
        else
          price = min_price_items[ eve_item.id ]
          daily_monthly_diff = (price / avg_price)-1 if price && avg_price
        end

        full_batch_size = [ eve_item.full_batch_size, volume_sum ].min
        margin = eve_item.margin( price )
        benef = ( full_batch_size * margin if full_batch_size && margin )
        benef_pcent = eve_item.pcent_margin( price )

        record_ok_for_user = !( (@user.min_pcent_for_advice && benef_pcent && benef_pcent < @user.min_pcent_for_advice/100.0) ||
            (@user.min_amount_for_advice && benef && benef < @user.min_amount_for_advice) )

        if record_ok_for_user

          region = trade_hub.region
          trade_hub_name = "#{trade_hub.name} (#{region.name})"
          region_name = "#{region.name } (#{region.trade_hubs.map{ |e| e.name }.join( ', ' )})"

          set_trade_hubs( trade_hub_name )
          set_regions_names( region_name )
          set_items( eve_item.name )

          price_record = {
            trade_hub: trade_hub_name,
            region_name: region_name,
            eve_item: eve_item.name,
            trade_hub_id: trade_hub.id,
            eve_item_id: eve_item.id,
            cpp_eve_item_id: eve_item.cpp_eve_item_id,
            cpp_system_id: trade_hub.eve_system_id,
            cost: eve_item.single_unit_cost,
            price: price,
            benef: benef,
            benef_pcent: benef_pcent,
            batch_size: eve_item.full_batch_size,
            monthly_amount: volume_sum,
            id: eve_item.id
          }

          if margin_type == :daily
            price_record[ :daily_monthly_diff ] = daily_monthly_diff
          end

          @prices_array << price_record

        end
      end
    end
    @prices_array.sort_by!{ |h| nvl( h[:benef] ) }
    @prices_array.reverse!

  end

end