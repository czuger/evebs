class ItemsController < ApplicationController

  # before_action :require_logged_in!
  before_action :set_user, :set_small_screen, :set_no_title_header, :set_show_update_weekly

  caches_page :show

  include Modules::Nvl
  include Modules::CheckedProductionListIds

  def show
    @item = EveItem.friendly.find( params[ :id ] )
    get_jita

    @meta_title = "Information about #{@item.name}"
    @meta_content = @item.description.truncate_words( 100 )

		@breadcrumb = @item.breadcrumb( view_context )
    # @jita_min_price = PricesMin.find_by_eve_item_id_and_trade_hub_id( @item.id, get_jita.id )
    # redirect_to item_market_overview_path( @item )
  end

end
