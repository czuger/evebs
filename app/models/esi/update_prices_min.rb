class Esi::UpdatePricesMin < Esi::Download

  def initialize( debug_request: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
  end

  # TODO : il faut gérer la disparition de l'ordre. Est ce qu'on s'en fout ?
  # Dans un premier temps oui, car on ne sait pas si l'ordre a été annulé, timeout ou bien vendu.
  def update( only_cpp_region_id = nil, cpp_type_id = nil )

    Banner.p 'About to update min prices'

    @trade_hubs = TradeHub.pluck( :eve_system_id ).to_set
    regions = Region.all

    @trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    @eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
    @cpp_type_id = cpp_type_id

    @sales_orders_ids = SalesOrder.pluck(:order_id, :volume ).to_set
    @sales_orders_stored = 0

    regions.each do |region|
      cpp_region_id = region.cpp_region_id.to_i

      next if only_cpp_region_id && only_cpp_region_id != cpp_region_id

      # next if internal_region_id < 24
      puts "Requesting #{region.name}" if @debug_request

      prices = {}
      puts "Requesting page #{@params[:page]}" if @params[:page] && @debug_request
      @rest_url = "markets/#{cpp_region_id}/orders/"

      pages = get_all_pages

      ActiveRecord::Base.transaction do
        prices = process_prices( pages, prices )
        # save_prices( prices)
        update_prices
      end

    end

    ActiveRecord::Base.transaction do
      Banner.p 'About to update volumes.'
      update_volumes
      SalesOrder.where( 'day < ?', Time.now - 1.month ).delete_all
    end

    puts "#{@sales_orders_stored} sales orders stored."
  end

  private

  def update_prices
    request = File.open( "#{Rails.root}/sql/update_prices_mins.sql" ).read
    ActiveRecord::Base.connection.execute( request )
  end

  def update_volumes
    PricesMin.all.each do |pm|
      pm.volume = SalesOrder.where( trade_hub_id: pm.trade_hub_id, eve_item_id: pm.eve_item_id, price: pm.min_price ).sum( :volume )
      pm.save!
    end
  end

  def process_prices( pages, prices )
    @sales_orders = []

    pages.each do |record|

      next unless @trade_hubs.include?(record['system_id'])

      next if @cpp_type_id && record['type_id'] != @cpp_type_id

      key = [record['system_id'], record['type_id']]
      # prices[key] ||= []
      # prices[key] << record['price']

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

    # prices.transform_values{ |v| v.min }
  end

  # def save_prices( prices )
  #   prices.each do |key, price|
  #     trade_hub_id = @trade_hub_conversion_hash[key[0]]
  #
  #     unless trade_hub_id
  #       puts "Trade hub not found for cpp id #{key[0]}" if @debug_request
  #       next
  #     end
  #
  #     eve_item_id = @eve_item_conversion_hash[key[1]]
  #     unless eve_item_id
  #       puts "Type id not found for cpp id #{key[1]}" if @debug_request
  #       next
  #     end
  #
  #     # puts "trade_hub_id = #{trade_hub_id}, eve_item_id = #{eve_item_id}" if @debug_request
  #
  #     mp = PricesMin.where(eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).first_or_initialize
  #     mp.min_price = price
  #     mp.save!
  #
  #     # computation will come from sales records.
  #
  #     # mpd = MinPriceDaily.where( eve_item_id: eve_item_id, trade_hub_id: trade_hub_id, day: Time.now ).first_or_initialize do |record|
  #     #   record.price = price
  #     # end
  #     # mpd.price = [ price, mpd.price ].min
  #     # mpd.save!
  #   end
  # end
end