module Modules::CheckedProductionListIds

  def set_checked_production_list_ids
    @checked_production_list_ids = current_user.production_lists.joins(
        'INNER JOIN prices_advices ON production_lists.trade_hub_id = prices_advices.trade_hub_id
          AND production_lists.eve_item_id = prices_advices.eve_item_id' )
                                       .pluck( 'prices_advices.id' )
  end

end