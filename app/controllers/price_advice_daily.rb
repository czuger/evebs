module PriceAdviceDaily

  def advice_prices
    @user = current_user
    @prices_array = []
    @no_concurent_array = []
    # This mean we already have an order for that item on that hub
    # TODO : add a catch there to check for eve api connection errors
    @fullfilled_orders = @user.get_occuped_places if @user.remove_occuped_places
    @item_count = {}

    @print_change_warning=print_change_warning
    @monthly_averages = get_montly_items_averages
    # pp @monthly_averages

    @user.trade_hubs.each do |trade_hub|
      eve_items = @user.eve_items.to_a

      eve_items.reject!{ |i| @fullfilled_orders.include?([trade_hub.id,i.id]) } if @user.remove_occuped_places

      min_price_items = MinPrice.includes(eve_item:[:blueprint]).where( { eve_item_id: eve_items.map{ |i| i.id }, trade_hub_id: trade_hub.id } )
      min_price_items.each do |min_price_item|

        if min_price_item && min_price_item.eve_item && min_price_item.eve_item.blueprint && min_price_item.eve_item.cost

          blueprint = min_price_item.eve_item.blueprint

          batch_size = blueprint.nb_runs*blueprint.prod_qtt
          batch_cost = min_price_item.eve_item.cost*blueprint.nb_runs
          batch_sell_price = min_price_item.min_price*batch_size
          benef = batch_sell_price - batch_cost
          benef_pcent = ((batch_sell_price*100) / batch_cost).round(0)-100

          record_ok_for_user = true
          if @user.min_pcent_for_advice && benef_pcent < @user.min_pcent_for_advice
            record_ok_for_user = false
          end
          if @user.min_amount_for_advice && benef < @user.min_amount_for_advice
            record_ok_for_user = false
          end

          if record_ok_for_user
            @item_count[min_price_item.eve_item.name]+=1 if @item_count.has_key?( min_price_item.eve_item.name )
            @item_count[min_price_item.eve_item.name]=1 unless @item_count.has_key?( min_price_item.eve_item.name )

            region_item_key = [[trade_hub.region_id],[min_price_item.eve_item_id]]
            # puts "Region item key = #{region_item_key.inspect}"

            price_record = {
              trade_hub: trade_hub.name,
              eve_item: min_price_item.eve_item.name,
              trade_hub_id: trade_hub.id,
              eve_item_id: min_price_item.eve_item_id,
              min_price: min_price_item.min_price.round(1),
              cost: (min_price_item.eve_item.cost/blueprint.prod_qtt).round(1),
              benef: benef,
              benef_pcent: benef_pcent,
              batch_size: batch_size,
            }

            if @monthly_averages && @monthly_averages[region_item_key]
              price_record[:monthly_amount] = @monthly_averages[region_item_key].volume_sum
              price_record[:monthly_avg_price] = @monthly_averages[region_item_key].avg_price_avg
              price_record[:monthly_low_price] = @monthly_averages[region_item_key].low_price_avg
              price_record[:diff_between_daily_min_and_monthly_min_pcent] = (min_price_item.min_price-@monthly_averages[region_item_key].low_price_avg)/ @monthly_averages[region_item_key].low_price_avg
            end

            @prices_array << price_record
          end
        else
          @prices_array << {
            trade_hub: trade_hub.name,
            eve_item: min_price_item.eve_item.name,
            min_price: 'NA',
            cost: 'NA',
            benef: 'NA',
            benef_pcent: 'NA',
            batch_size: 'NA'
          }
        end
      end
      no_orders_items = eve_items - min_price_items.map{ |mpi| mpi.eve_item }
      @no_concurent_array += no_orders_items.map{ |noi| { trade_hub: trade_hub.name, eve_item: noi.name } }
    end

    @prices_array.sort_by!{ |h| h[:benef] }
    @prices_array.reverse!
  end

end