class ItemsController < ApplicationController

  include Modules::PriceAdvices::ShowItemDetail
  include Modules::Nvl

  def cost
    @item = EveItem.find( params[ :item_id ] )
  end

end
