class RemoveProductionListShareRequest < ActiveRecord::Migration[5.2]
  def change
    drop_table :production_list_share_requests
  end
end
