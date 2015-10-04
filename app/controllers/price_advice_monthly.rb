module PriceAdviceMonthly

  def advice_prices_monthly
    @user = current_user
    @prices_array = []
    @item_count = {}
    @monthly_averages = get_montly_items_averages
    @shopping_basket = get_shopping_basket
    # pp @monthly_averages

    user_eve_items = @user.eve_items.includes( :blueprint )

    @user.trade_hubs.each do |trade_hub|

      eve_items = user_eve_items
      if @user.remove_occuped_places
        eve_items = user_eve_items.where.not( id: trade_hub.get_selling_eve_items_ids( @user ) )
      end

      eve_items.find_each do |eve_item|

        region_item_key = [[trade_hub.region_id],[eve_item.id]]

        avg_price = volume_avg = order_count_avg = benef = benef_pcent = nil
        if @monthly_averages && @monthly_averages[region_item_key]
          avg_price = @monthly_averages[region_item_key].avg_price_avg
          volume_avg = @monthly_averages[region_item_key].volume_avg
          order_count_avg = @monthly_averages[region_item_key].order_count_avg
        end

        if eve_item && avg_price
          benef = eve_item.margin( avg_price ) * eve_item.full_batch_size
          benef_pcent = eve_item.pcent_margin( avg_price )
        end

        record_ok_for_user = true
        if @user.min_pcent_for_advice && benef_pcent && benef_pcent < @user.min_pcent_for_advice/100.0
          record_ok_for_user = false
        end
        if @user.min_amount_for_advice && benef && benef < @user.min_amount_for_advice
          record_ok_for_user = false
        end

        if record_ok_for_user

          set_trade_hubs( trade_hub.name )
          set_items( eve_item.name )

          price_record = {
            trade_hub: trade_hub.name,
            eve_item: eve_item.name,
            trade_hub_id: trade_hub.id,
            eve_item_id: eve_item.id,
            avg_price: avg_price,
            cost: eve_item.single_unit_cost,
            benef: benef,
            benef_pcent: benef_pcent,
            batch_size: eve_item.full_batch_size,
            volume_avg: volume_avg,
            order_count_avg: order_count_avg
          }

          @prices_array << price_record
        end
      end
    end
    @prices_array.sort_by!{ |h| (h[:benef] ? h[:benef] : -Float::INFINITY) }
    @prices_array.reverse!

  end

end