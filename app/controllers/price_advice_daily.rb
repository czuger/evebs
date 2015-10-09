module PriceAdviceDaily

  def advice_prices
    @user = current_user
    @prices_array = []
    @no_concurent_array = []
    # This mean we already have an order for that item on that hub
    # TODO : add a catch there to check for eve api connection errors
    @fullfilled_orders = @user.get_occuped_places if @user.remove_occuped_places

    @print_change_warning=print_change_warning
    @monthly_averages = get_montly_items_averages
    # pp @monthly_averages
    @shopping_basket = get_shopping_basket

    @user.trade_hubs.each do |trade_hub|

      set_trade_hubs( trade_hub.name )

      eve_items = @user.eve_items.to_a

      eve_items.reject!{ |i| @fullfilled_orders.include?([trade_hub.id,i.id]) } if @user.remove_occuped_places

      min_price_items = MinPrice.includes(eve_item:[:blueprint]).where( { eve_item_id: eve_items.map{ |i| i.id }, trade_hub_id: trade_hub.id } )
      min_price_items.each do |min_price_item|

        if min_price_item && min_price_item.eve_item && min_price_item.eve_item.blueprint && min_price_item.eve_item.cost

          eve_item = min_price_item.eve_item

          if eve_item
            benef = eve_item.margin( min_price_item.min_price ) * eve_item.full_batch_size
            benef_pcent = eve_item.pcent_margin( min_price_item.min_price )
          end

          record_ok_for_user = true
          if @user.min_pcent_for_advice && benef_pcent < @user.min_pcent_for_advice/100.0
            record_ok_for_user = false
          end
          if @user.min_amount_for_advice && benef < @user.min_amount_for_advice
            record_ok_for_user = false
          end

          if record_ok_for_user

            set_trade_hubs( trade_hub.name )
            set_items( eve_item.name )

            region_item_key = [[trade_hub.region_id],[min_price_item.eve_item_id]]
            # puts "Region item key = #{region_item_key.inspect}"

            avg_price = volume_avg = order_count_avg = benef = benef_pcent = nil
            if @monthly_averages && @monthly_averages[region_item_key]
              avg_price = @monthly_averages[region_item_key].avg_price_avg
              volume_avg = @monthly_averages[region_item_key].volume_avg
              volume_sum = @monthly_averages[region_item_key].volume_sum
              order_count_avg = @monthly_averages[region_item_key].order_count_avg
              diff_between_daily_min_and_monthly_min_pcent = (min_price_item.min_price-avg_price)/avg_price
            end

            price_record = {
              trade_hub: trade_hub.name,
              eve_item: eve_item.name,
              trade_hub_id: trade_hub.id,
              eve_item_id: eve_item.id,
              min_price: min_price_item.min_price,
              cost: eve_item.single_unit_cost,
              benef: benef,
              benef_pcent: benef_pcent,
              batch_size: eve_item.full_batch_size,
            }

            if @monthly_averages && @monthly_averages[region_item_key]
              price_record[:monthly_avg] = volume_avg
              price_record[:monthly_amount] = volume_sum
              price_record[:monthly_avg_price] = avg_price
              price_record[:monthly_low_price] = order_count_avg
              price_record[:diff_between_daily_min_and_monthly_min_pcent] = diff_between_daily_min_and_monthly_min_pcent
            end

            @prices_array << price_record
          end
        end
      end
      no_orders_items = eve_items - min_price_items.map{ |mpi| mpi.eve_item }
      @no_concurent_array += no_orders_items.map{ |noi| { trade_hub: trade_hub.name, eve_item: noi.name } }
    end

    @prices_array.sort_by!{ |h| nvl( h[:benef] ) }
    @prices_array.reverse!

  end

end