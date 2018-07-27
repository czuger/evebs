require_relative 'download'

# Seems not to require full download of all prices history
# Just jita, see ...
class Esi::UpdateVolumeFromHistory < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update
    Banner.p 'About to update the table eve_markets_histories'

    the_forge_cpp_id = '10000002'

    ActiveRecord::Base.transaction do
      EveItem.pluck( 'cpp_eve_item_id' ).each do |cpp_id|

        @rest_url = "markets/#{the_forge_cpp_id}/history/"
        @params[:type_id]=cpp_id
        pages = get_all_pages

        pages.reject!{ |e| DateTime.parse( e['date'] ) < Time.now - 1.month }
        total_volume = pages.map{ |e| e['volume'] }.reduce( :+ )

        pa = PricesAdvice.joins( :eve_item, { trade_hub: :region } ).where( 'eve_items.cpp_eve_item_id' => cpp_id )
                 .where( 'regions.cpp_region_id' => the_forge_cpp_id ).first

        pa.update!( history_volume: total_volume )
      end
    end
  end

end