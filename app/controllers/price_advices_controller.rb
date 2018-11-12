require 'time_diff'

class PriceAdvicesController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, :set_wide_screen, :set_show_update_hourly

  include Modules::PriceAdvices::MarginModule
  include Modules::Nvl
  include Modules::CheckedProductionListIds

  def advice_prices_weekly
    @title = 'Show rentability with sell orders - weekly average'
    advice_prices_margins( :weekly )
  end

  def advice_prices
    @title = 'Show rentability with sell orders - immediate price'
    advice_prices_margins( :daily )
  end

  def empty_places
    @empty_places_objects = PriceAdvicesMinPrice.where( min_price: nil ).where.not( vol_month: nil )
      .order( 'vol_month DESC' ).paginate(:page => params[:page], :per_page => 20 )

    @empty_places_array = @empty_places_objects
      .pluck_to_hash( :trade_hub_name, :item_name, :eve_item_id, :vol_month, :avg_price_month, :cost )
  end

  private

end

