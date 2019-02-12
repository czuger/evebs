require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadHistory < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update
    Misc::Banner.p 'About to update the table eve_market_histories'

    Region.all.each do |region|
      puts "Processing region #{region.name}"
      ActiveRecord::Base.transaction do
        update_for_given_region region
      end
    end

    EveMarketHistory.where( 'server_date <= ?', Time.now - 1.month ).delete_all
  end

  def update_for_given_region( region )

    @rest_url = "markets/#{region.cpp_region_id}/types/"
    types_ids = get_all_pages

    puts "#{types_ids.count} to process"

    database_cpp_items_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]

    types_ids.select!{ |t| database_cpp_items_hash[t] }

    puts "#{types_ids.count} in database"

    types_ids.each do |type_id|

      item_id = database_cpp_items_hash[type_id]

      @rest_url = "markets/#{region.cpp_region_id}/history/"
      @params[:type_id]=type_id

      get_all_pages.each do |record|

        # p record['date']
        # p Date.parse(record['date'])

        next if Date.parse(record['date']) <= Time.now - 1.month

        evm = EveMarketHistory.where(region_id: region.id, eve_item_id: item_id, server_date: record['date'] ).first_or_initialize

        # p record
        evm.volume = record['volume']
        evm.order_count = record['order_count']
        evm.highest = record['highest']
        evm.lowest = record['lowest']
        evm.average = record['average']

        evm.save!
      end
    end

  end

end