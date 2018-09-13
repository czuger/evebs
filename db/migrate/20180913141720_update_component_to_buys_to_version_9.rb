class UpdateComponentToBuysToVersion9 < ActiveRecord::Migration[5.2]
  def change
    update_view :component_to_buys, version: 9, revert_to_version: 8
  end
end
