class Esi::DownloadSalesOrders < Esi::Download

  def initialize( debug_request: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
  end

  # il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
  # Dans un premier temps oui (oui, on s'en fout), car on ne sait pas
  # si l'ordre a été annulé, timeout ou bien vendu.
  def update( only_cpp_region_id = nil, cpp_type_id = nil )

    Banner.p 'About to update min prices'

    @trade_hubs = TradeHub.pluck( :eve_system_id ).to_set
    regions = Region.all

    @trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    @eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
    @cpp_type_id = cpp_type_id

    @sales_orders_ids = SalesOrder.pluck(:order_id, :volume ).to_set
    @sales_orders_stored = 0

    ActiveRecord::Base.transaction do

      regions.each do |region|
        cpp_region_id = region.cpp_region_id.to_i

        next if only_cpp_region_id && only_cpp_region_id != cpp_region_id

        # next if internal_region_id < 24
        puts "Requesting #{region.name}" if @debug_request

        puts "Requesting page #{@params[:page]}" if @params[:page] && @debug_request
        @rest_url = "markets/#{cpp_region_id}/orders/"

        pages = get_all_pages
        download_orders( pages )
      end

      SalesOrder.where( 'day < ?', Time.now - 1.month ).delete_all

    end

    puts "#{@sales_orders_stored} sales orders stored."
  end

  private

  def download_orders( pages )
    @sales_orders = []

    pages.each do |record|

      next unless @trade_hubs.include?(record['system_id'])

      next if @cpp_type_id && record['type_id'] != @cpp_type_id

      key = [record['system_id'], record['type_id']]

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
                                        trade_hub_id: trade_hub_id, eve_item_id: eve_item_id, order_id: record['order_id'])

        @sales_orders_stored += 1
        @sales_orders_ids << sale_key
      end
    end

    SalesOrder.import @sales_orders
  end
end