class ItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  include Modules::PriceAdvices::ShowItemDetail
  include Modules::Nvl

  def cost
    @item = EveItem.find_by( id: params[ :item_id ] )
  end

end
