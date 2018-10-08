class UpdateComponentsToBuysToVersion3 < ActiveRecord::Migration[5.2]
  def change
    update_view :components_to_buys, version: 2, revert_to_version: 1
  end
end
