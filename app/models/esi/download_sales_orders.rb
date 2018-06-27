class Esi::DownloadSalesOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
  end

  # il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
  # Dans un premier temps oui (oui, on s'en fout), car on ne sait pas
  # si l'ordre a été annulé, timeout ou bien vendu.
  def update( only_cpp_region_id: nil, cpp_type_id: nil )

    Banner.p 'About to update min prices'

    @trade_hubs = TradeHub.pluck( :eve_system_id ).to_set
    regions = Region.all

    @trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    @eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
    @cpp_type_id = cpp_type_id

    @sales_orders_ids = SalesOrder.pluck(:order_id, :volume ).to_set
    @order_ids_present = []
    puts "@sales_orders_ids.count = #{@sales_orders_ids.count}" if @debug_request

    @sales_orders_stored = 0

    @sequence = ActiveRecord::Sequence.new('sales_orders_retrieve_session_id' )
    @sales_orders_retrieve_session_id = @sequence.next

    puts "@sales_orders_retrieve_session_id = #{@sales_orders_retrieve_session_id}" if @debug_request

    ActiveRecord::Base.transaction do

      BlueprintComponentSalesOrder.update_all( touched: false )

      regions.each do |region|
        cpp_region_id = region.cpp_region_id.to_i

        # puts "only_cpp_region_id=#{only_cpp_region_id} vs cpp_region_id=#{cpp_region_id}" if @debug_request

        next if only_cpp_region_id && only_cpp_region_id != cpp_region_id

        # next if internal_region_id < 24
        puts "Requesting #{region.name}" if @debug_request

        puts "Requesting page #{@params[:page]}" if @params[:page] && @debug_request
        @rest_url = "markets/#{cpp_region_id}/orders/"

        pages = get_all_pages
        download_orders( pages )

      end

      @order_ids_present.uniq!

      # Remove after first test.
      SalesOrder.update_all( closed: false )

      orders_absent = SalesOrder.distinct.pluck( :order_id ) - @order_ids_present

      orders_absent.in_groups_of( 10000 ) do |g|
        SalesOrder.where( order_id: g.compact ).update_all( closed: true )
      end

      SalesOrder.where( 'day < ?', Time.now - 1.month ).delete_all

      BlueprintComponentSalesOrder.where(  touched: false ).delete_all

      bc_update_statement = File.open( 'sql/update_component_raw_cost.sql', 'r' ).read
      BlueprintComponent.exec_update( bc_update_statement )
    end

    puts "#{@sales_orders_stored} sales orders stored."
  end

  private

  def download_orders( pages )
    @sales_orders = []

    pages.each do |record|

      next unless @trade_hubs.include?(record['system_id'])

      next if @cpp_type_id && record['type_id'] != @cpp_type_id

      update_blueprint_component_sales_orders( record )

      sale_key = [ record['order_id'], record['volume_remain'] ]
      unless @sales_orders_ids.include?( sale_key )

        trade_hub_id = @trade_hub_conversion_hash[record['system_id']]
        unless trade_hub_id
          puts "Trade hub not found for cpp id #{record['system_id']}"
          next
        end

        eve_item_id = @eve_item_conversion_hash[record['type_id']]
        unless eve_item_id
          puts "Type id not found for cpp id #{record['type_id']}" if @debug_request
          next
        end

        @sales_orders << SalesOrder.new(day: Time.now, volume: record['volume_remain'], price: record['price'],
          trade_hub_id: trade_hub_id, eve_item_id: eve_item_id, order_id: record['order_id'],
          retrieve_session_id: @sales_orders_retrieve_session_id, closed: false )

        @sales_orders_stored += 1
        @sales_orders_ids << sale_key

        if @sales_orders.count == 2000
          SalesOrder.import!( @sales_orders )
          @sales_orders = []
        end
      end

      @order_ids_present << record['order_id']
    end

    SalesOrder.import @sales_orders
  end

  def update_blueprint_component_sales_orders( record )

    trade_hub_id = @trade_hub_conversion_hash[record['system_id']]
    bc = BlueprintComponent.find_by_cpp_eve_item_id( record['type_id'] )

    if bc
      bc_so = BlueprintComponentSalesOrder.where( cpp_order_id: record['order_id'] ).first_or_initialize

      bc_so.trade_hub_id = trade_hub_id
      bc_so.blueprint_component_id = bc.id

      bc_so.volume = record['volume_remain']
      bc_so.price = record['price']
      bc_so.touched = true

      bc_so.save!
    end

  end

end