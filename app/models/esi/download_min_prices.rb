class Esi::DownloadMinPrices < Esi::Download

  def initialize( debug_request: false )
    super( nil, { order_type: :sell }, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def dl

    trade_hubs = TradeHub.pluck( :eve_system_id ).to_set
    regions = Region.pluck( :id, :cpp_region_id )

    regions.each do |region|
      internal_region_id, cpp_region_id = region
      next if internal_region_id < 12
      puts "Requesting #{internal_region_id}"
      cpp_region_id = cpp_region_id.to_i

      prices = {}
      loop do
        puts "Requesting page #{@params[:page]}" if @params[:page]
        @rest_url = "markets/#{cpp_region_id}/orders/"
        pages = get_page

        unless pages.is_a? Array
          puts [ pages, @errors_limit_remain.to_s, @errors_limit_reset.to_s ].join( ', ' ) if @debug_request
          next
        end

        # pp pages

        break if pages.empty?

        pages.each do |record|
          next unless trade_hubs.include?(record['system_id'])
          prices[record['type_id']] ||= []
          prices[record['type_id']] << record['price']
        end

        # pp @pages_count, @params

        break if @pages_count == 1

        if @pages_count > 1
          p @pages_count
          unless @params[:page]
            @params[:page] = 2
          else
            @params[:page] += 1
          end

        end

        if @params[:page] && @params[:page] > @pages_count
          @params.delete(:page)
          break
        end

      end

      p prices.count if prices.count > 0

    end
  end



end