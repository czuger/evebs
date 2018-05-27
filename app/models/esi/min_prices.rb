class Esi::MinPrices < Esi::Download

  def initialize( debug_request: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update

    trade_hubs = TradeHub.pluck( :eve_system_id ).to_set
    regions = Region.all

    trade_hub_conversion_hash = Hash[ TradeHub.pluck( :eve_system_id, :id ) ]
    eve_item_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]

    regions.each do |region|
      cpp_region_id = region.cpp_region_id

      # next if internal_region_id < 24
      puts "Requesting #{region.name}" if @debug_request
      cpp_region_id = cpp_region_id.to_i

      prices = {}
      puts "Requesting page #{@params[:page]}" if @params[:page] && @debug_request
      @rest_url = "markets/#{cpp_region_id}/orders/"

      pages = get_all_pages

      pages.each do |record|
        next unless trade_hubs.include?(record['system_id'])
        key = [record['system_id'], record['type_id']]
        prices[key] ||= []
        prices[key] << record['price']
      end

      prices.transform_values!{ |v| v.min }

      ActiveRecord::Base.transaction do
        prices.each do |key, price|
          trade_hub_id = trade_hub_conversion_hash[key[0]]
          puts "Trade hub not found for cpp id #{key[0]}" unless trade_hub_id if @debug_request

          eve_item_id = eve_item_conversion_hash[key[1]]
          unless eve_item_id
            puts "Type id not found for cpp id #{key[1]}" if @debug_request
            next
          end

          # puts "trade_hub_id = #{trade_hub_id}, eve_item_id = #{eve_item_id}" if @debug_request

          mp = MinPrice.where( eve_item_id: eve_item_id, trade_hub_id: trade_hub_id ).first_or_initialize do |p|
            p.min_price = price
          end

          mp.save!

        end
      end

    end
  end



end