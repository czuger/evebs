class UpdateComponentToBuysToVersion3 < ActiveRecord::Migration[5.2]
  def change
    update_view :component_to_buys, version: 3, revert_to_version: 2
  end
end
