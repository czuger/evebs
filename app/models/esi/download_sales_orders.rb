class Esi::DownloadSalesOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
  end

  # il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
  # Dans un premier temps oui (oui, on s'en fout), car on ne sait pas
  # si l'ordre a été annulé, timeout ou bien vendu.
  def update

    Banner.p 'About to update min prices'

    @trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    @eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]

    @sales_orders_created = 0
    @sales_orders_updated = 0

    ActiveRecord::Base.transaction do

      BlueprintComponentSalesOrder.update_all( touched: false )
      SalesOrder.update_all( touched: false )

      Region.all.each do |region|
        cpp_region_id = region.cpp_region_id.to_i

        # puts "only_cpp_region_id=#{only_cpp_region_id} vs cpp_region_id=#{cpp_region_id}" if @debug_request

        # next if internal_region_id < 24
        puts "Requesting #{region.name}" if @debug_request
        puts "Requesting page #{@params[:page]}" if @params[:page] && @debug_request

        @rest_url = "markets/#{cpp_region_id}/orders/"
        pages = get_all_pages

        pages.each do |record|
          trade_hub_id = @trade_hub_conversion_hash[record['system_id']]
          next unless trade_hub_id

          update_sales_orders( trade_hub_id, record )
          update_blueprint_component_sales_orders( trade_hub_id, record )
        end
      end

      SalesOrder.where( touched: false ).delete_all
      SalesFinal.where( 'updated_at < ?', Time.now - 1.month ).delete_all

      BlueprintComponentSalesOrder.where( touched: false ).delete_all
      BpcJitaSalesFinal.where( 'updated_at < ?', Time.now - 1.week ).delete_all
    end

    puts "Sales orders created : #{@sales_orders_stored}"
    puts "Sales orders updated : #{@sales_orders_updated}"
  end

  private

  def update_sales_orders( trade_hub_id, record )

    eve_item_id = @eve_item_conversion_hash[record['type_id']]
    return unless eve_item_id

    so = SalesOrder.where( order_id: record['order_id'] ).first

    if so
      # If volume is unchanged, then we just touch the order
      if so.volume != record['volume_remain']
        # Volume has changed, we create a sales final record
        volume = so.volume - record['volume_remain']
        price = (so.price + record['price']) / 2.0

        create_sales_final_record( so, so.volume, record['volume_remain'], so.price,
                                   record['price'] )

        so.volume = record['volume_remain']
        so.price = record['price']
      end
      so.touched = true
      so.save!

      @sales_orders_updated += 1

    else
      # We still do not have a SaleOrder with this
      so = SalesOrder.create!( day: Time.now, volume: record['volume_remain'], price: record['price'],
                          trade_hub_id: trade_hub_id, eve_item_id: eve_item_id, order_id: record['order_id'],
                          touched: true )

      @sales_orders_created += 1

      # If we start with a different volume than the initial volume, that mean we missed some selling
      if record['volume_remain'] != record['volume_total']
        create_sales_final_record( so, record['volume_total'], record['volume_remain'],
                                   record['price'], record['price'] )
      end
    end
  end

  def create_sales_final_record( so, old_volume, new_volume, old_price, new_price )
    volume = old_volume - new_volume
    price = (old_price + new_price) / 2.0

    SalesFinal.create!(
        day: so.day, trade_hub_id: so.trade_hub_id, eve_item_id: so.eve_item_id, volume: volume, price: price,
        order_id: so.order_id )
  end

  def update_blueprint_component_sales_orders( trade_hub_id, record )

    bc = BlueprintComponent.find_by_cpp_eve_item_id( record['type_id'] )

    if bc
      # Recording the current blueprint
      older_bc_so = BlueprintComponentSalesOrder.where( cpp_order_id: record['order_id'] ).first
      if older_bc_so
        # We already have an order, we will update it and store the difference
        if older_bc_so.volume != record['volume_remain']

          # save the diff into bpc_jita_sales_finals if it is done in jita
          if record['system_id'] == 30000142
            sold_volume = older_bc_so.volume - record['volume_remain']
            sold_price = record['price']
            BpcJitaSalesFinal.create!( blueprint_component_id: bc.id, volume: sold_volume, price: sold_price,
                                       cpp_order_id: record['order_id'] )
          end

          older_bc_so.volume = record['volume_remain']
          older_bc_so.price = record['price']
        end

        older_bc_so.touched = true
        older_bc_so.save!
      else
        BlueprintComponentSalesOrder.create!( cpp_order_id: record['order_id'], volume: record['volume_remain'],
           price: record['price'], touched: true, trade_hub_id: trade_hub_id, blueprint_component_id: bc.id )
      end
    end
  end
end