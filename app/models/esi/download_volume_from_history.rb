require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::DownloadVolumeFromHistory < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update
    Banner.p 'About to update the table eve_market_volumes'

    regions_volumes = {}

    Region.all.each do |region|
      @volume_for_region = 0

      ActiveRecord::Base.transaction do
        update_for_given_region region
      end

      regions_volumes[ region.name ] = @volume_for_region
    end

    pp regions_volumes
  end

  def update_for_given_region( region )

    @rest_url = "markets/#{region.cpp_region_id}/types/"
    types_ids = get_all_pages
    database_cpp_items_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]

    types_ids.select!{ |t| database_cpp_items_hash[t] }

    types_ids.each do |type_id|

      item_id = database_cpp_items_hash[type_id]

      @rest_url = "markets/#{region.cpp_region_id}/history/"
      @params[:type_id]=type_id

      get_all_pages.each do |record|
        evm = EveMarketVolume.where( region_id: region.id, eve_item_id: item_id ).first_or_initialize

        # p record
        evm.volume = record['volume']
        evm.save!

        @volume_for_region += evm.volume
      end
    end

    # EveItem.pluck( 'cpp_eve_item_id' ).each do |cpp_id|
    #
    #   @rest_url = "markets/#{the_forge_cpp_id}/types/"
    #
    #
    #
    #   @params[:type_id]=cpp_id
    #
    #   begin
    #     pages = get_all_pages
    #
    #     pages.reject!{ |e| DateTime.parse( e['date'] ) < Time.now - 1.month }
    #     total_volume = pages.map{ |e| e['volume'] }.reduce( :+ )
    #
    #     pa = PricesAdvice.joins( :eve_item, { trade_hub: :region } ).where( 'eve_items.cpp_eve_item_id' => cpp_id )
    #              .where( 'regions.cpp_region_id' => the_forge_cpp_id ).first
    #
    #     pa.update!( history_volume: total_volume )
    #   rescue Esi::Errors::NotFound
    #     # we don't care ...
    #   end
    #
    # end
  end

end