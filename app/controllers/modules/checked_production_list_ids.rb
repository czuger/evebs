module Modules::CheckedProductionListIds

  def set_checked_production_list_ids
    @checked_production_list_ids = current_user.production_lists.pluck( :trade_hub_id, :eve_item_id ).to_set
  end

end