class Esi::DownloadSalesOrders < Esi::Download

  def initialize( debug_request: false, silent_output: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
    @silent_output = silent_output
  end

  # il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
  # Dans un premier temps oui (oui, on s'en fout), car on ne sait pas
  # si l'ordre a été annulé, timeout ou bien vendu.
  def update

    Banner.p 'About to update min prices' unless @silent_output

    @trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    @eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
    @blueprint_component_conversion_hash = Hash[ BlueprintComponent.pluck( :cpp_eve_item_id, :id ) ]

    @sales_orders_created = 0
    @sales_orders_updated = 0
    @sales_orders_deleted = 0

    @sales_orders_over_time = 0

    @sales_finals_created = 0
    sales_finals_deleted = 0

    @sales_orders_volumes = Hash[ SalesOrder.pluck( :order_id, :volume ) ]
    @sales_orders_to_touch = []

    @blueprints_sales_orders_volumes = Hash[ BlueprintComponentSalesOrder.pluck( :cpp_order_id, :volume ) ]
    @blueprints_sales_orders_to_touch = []

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

        begin
          pages = get_all_pages
        rescue Esi::Errors::NotFound
          puts "Unable to find data for region #{region.name}"

          # In case we couldn' find data for region, we prevent removing untouched data (cos nothing will be touched for this region)
          SalesOrder.where( trade_hub_id: region.trade_hub_ids ).update_all( touched: true, updated_at: Time.now )
          BlueprintComponentSalesOrder.where( trade_hub_id: region.trade_hub_ids ).update_all( touched: true, updated_at: Time.now )

          next
        end

        orders_to_process_hash = {}

        # pp pages

        pages.sort_by { |e| e['volume'] }.reverse.each do |record|
          trade_hub_id = @trade_hub_conversion_hash[record['system_id']]
          next unless trade_hub_id

          update_sales_orders( trade_hub_id, record )
          update_blueprint_component_sales_orders( trade_hub_id, record )
        end

      end

      touch_unchanged_sales_orders
      remove_old_sales_orders

      sales_finals_to_delete = SalesFinal.where( 'updated_at < ?', Time.now - 1.month )
      sales_finals_deleted = sales_finals_to_delete.count
      sales_finals_to_delete.delete_all

      BlueprintComponentSalesOrder.where( touched: false ).delete_all
      BpcJitaSalesFinal.where( 'updated_at < ?', Time.now - 1.week ).delete_all

      # Temporary to remove unused users.
      UserSaleOrder.distinct.pluck( :user_id ).each do |uid|
        UserSaleOrder.where( user_id: uid ).delete_all unless User.where( id: uid ).exists?
      end

    end

    puts "Sales orders created : #{@sales_orders_created}" unless @silent_output
    puts "Sales orders updated : #{@sales_orders_updated}" unless @silent_output
    puts "Sales orders deleted : #{@sales_orders_deleted}" unless @silent_output
    puts "Sales orders that failed out of time : #{@sales_orders_over_time}" unless @silent_output

    puts "Sales final created : #{@sales_finals_created}" unless @silent_output
    puts "Sales final deleted : #{sales_finals_deleted}" unless @silent_output
  end

  private

  def update_sales_orders( trade_hub_id, record )

    eve_item_id = @eve_item_conversion_hash[record['type_id']]
    return unless eve_item_id

    sov = @sales_orders_volumes[ record['order_id'] ]

    if sov
      # If volume is unchanged, then we just touch the order

      issued = DateTime.parse( record['issued'] )
      duration = record['duration']
      end_time = issued + duration.days

      if sov != record['volume_remain']

        so = SalesOrder.where( order_id: record['order_id'] ).first

        # Volume has changed, we create a sales final record
        volume = so.volume - record['volume_remain']
        price = (so.price + record['price']) / 2.0

        create_sales_final_record( so, so.volume, record['volume_remain'], so.price,
                                   record['price'] )

        so.volume = record['volume_remain']
        so.price = record['price']
        so.touched = true
        so.issued = issued
        so.duration = duration
        so.end_time = end_time
        so.save!

        @sales_orders_updated += 1
      else
        @sales_orders_to_touch << record['order_id']
      end

    else
      # We still do not have a SaleOrder with this
      so = SalesOrder.create!( day: Time.now, volume: record['volume_remain'], price: record['price'],
                          trade_hub_id: trade_hub_id, eve_item_id: eve_item_id, order_id: record['order_id'],
                          touched: true, issued: issued, duration: duration, end_time: end_time )

      @sales_orders_volumes[ so.order_id ] = so.volume

      @sales_orders_created += 1

      # If we start with a different volume than the initial volume, that mean we missed some selling
      if record['volume_remain'] != record['volume_total']
        create_sales_final_record( so, record['volume_total'], record['volume_remain'],
                                   record['price'], record['price'] )
      end
    end
  end

  def touch_unchanged_sales_orders
    @sales_orders_to_touch.in_groups_of( 5000 ).each do |order_ids|
      SalesOrder.where( order_id: order_ids ).update_all( touched: true )
    end
    @blueprints_sales_orders_to_touch.in_groups_of( 5000 ).each do |order_ids|
      BlueprintComponentSalesOrder.where( cpp_order_id: order_ids ).update_all( touched: true, updated_at: Time.now )
    end
  end

  def remove_old_sales_orders
    # We assume that all old orders are closed as selling. We will have to estimate the orders that failed.
    SalesOrder.where( touched: false ).where( 'end_time < ?', Time.now ).each do |old_order|
      # pp old_order
      create_sales_final_record( old_order, old_order.volume, 0, old_order.price,
      old_order.price )
    end

    @sales_orders_over_time = SalesOrder.where( touched: false ).where( 'end_time >= ?', Time.now ).count

    sales_orders_to_delete = SalesOrder.where( touched: false )
    @sales_orders_deleted = sales_orders_to_delete.count
    sales_orders_to_delete.delete_all
  end

  def create_sales_final_record( so, old_volume, new_volume, old_price, new_price )
    volume = old_volume - new_volume
    price = (old_price + new_price) / 2.0

    SalesFinal.create!(
        day: Time.now, trade_hub_id: so.trade_hub_id, eve_item_id: so.eve_item_id, volume: volume, price: price,
        order_id: so.order_id )

    @sales_finals_created += 1
  end

  def update_blueprint_component_sales_orders( trade_hub_id, record )

    bc_id = @blueprint_component_conversion_hash[ record['type_id'] ]
    return unless bc_id

    # Recording the current blueprint
    bp_sov = @blueprints_sales_orders_volumes[ record['order_id'] ]
    if bp_sov
      # We already have an order, we will update it and store the difference
      if bp_sov != record['volume_remain']

        older_bc_so = BlueprintComponentSalesOrder.where( cpp_order_id: record['order_id'] ).first

        # save the diff into bpc_jita_sales_finals if it is done in jita
        if record['system_id'] == 30000142
          sold_volume = older_bc_so.volume - record['volume_remain']
          sold_price = record['price']
          BpcJitaSalesFinal.create!( blueprint_component_id: bc_id, volume: sold_volume, price: sold_price,
                                     cpp_order_id: record['order_id'] )
        end

        older_bc_so.volume = record['volume_remain']
        older_bc_so.price = record['price']
        older_bc_so.touched = true
        older_bc_so.save!
      else
        @blueprints_sales_orders_to_touch << record['order_id']
      end

    else
      bc_so = BlueprintComponentSalesOrder.create!( cpp_order_id: record['order_id'], volume: record['volume_remain'],
         price: record['price'], touched: true, trade_hub_id: trade_hub_id, blueprint_component_id: bc_id )

      @blueprints_sales_orders_volumes[ bc_so.cpp_order_id ] = bc_so.volume
    end
  end
end