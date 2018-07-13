module Modules::PriceAdvices::ShoppingBasketsModule

  def get_shopping_basket
    ProductionList.where(user_id: @user.id ).pluck(:trade_hub_id, :eve_item_id ).map{ |e| [@user.id, e ].flatten }
  end

end