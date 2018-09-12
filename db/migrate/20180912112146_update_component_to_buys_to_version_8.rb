class UpdateComponentToBuysToVersion8 < ActiveRecord::Migration[5.2]
  def change
    update_view :component_to_buys, version: 8, revert_to_version: 7
  end
end
